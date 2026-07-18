# PR Report Workflow

This is the detailed step sequence that the `pr-report` skill follows. It is a concrete breakdown of the high-level phases described in `SKILL.md`.

## Phase 1: Initialize

1. **Load config and state** — read `{config_dir}/pr-report.yaml`, `{config_dir}/shared.yaml`, and `{context_dir}/pr-report/{key}/state.md` if they exist. `{config_dir}` and `{context_dir}` are discovered by `detect-project-context`.
2. **Detect project context** — identify project root, config directory, context directory, and recommended defaults.
3. **Validate PR capability** — ensure at least one PR source tool is available and its token resolves. If no tool is detected, stop and consult the user.
4. **Migrate old config if present** — if the loaded config uses the old adapter-shaped schema (`adapters.{role}.source`), map it to the new provider-shaped schema (`pr-report.tools.{capability}.provider`) and persist the migrated config.

**Completion criterion:** `{config_dir}/pr-report.yaml` exists, the PR capability has a selected tool, and its token resolves without error.

## Phase 2: Resolve PR

1. **Invoke `identity-resolver/scripts/resolve-identity.py`** with the user input, optional repo/branch hints, and project context. If it returns `needs_input`, ask the user for a PR number or URL. If it returns a `ticket` type, search open PRs for a matching title or branch and ask the user if multiple match. If it returns a `branch` type, search for a PR whose head matches the branch.
2. **Identify repo and branch** — use the `repo`, `branch`, `base`, `commit`, and `url` fields from the identity envelope. Fall back to detecting `owner/repo` from the git remote and the current branch from git state only if the envelope does not provide them.
3. **Record state** — write `pr_number`, `repo`, `branch`, `base`, `commit`, `url`, and `key` to `{context_dir}/pr-report/{key}/state.md`.

**Completion criterion:** `pr_number`, `repo`, `branch`, and `key` are recorded in state.

## PR resolution ambiguity rules

See [REFERENCE.md](REFERENCE.md#pr-resolution-ambiguity-rules) for the canonical ambiguity rules (multiple PRs per ticket, no open PR, PR URLs, forks, ambiguous remotes).

## Phase 2a: Check prior context

1. **Query chainlog** — invoke `chainlog/query_latest` for the work item (`work_item_type: pr`, `work_item_key: {key}`) for each capability. Check each returned observation with `artifact-freshness`. Reuse fresh observations as the baseline for delta computation; record stale ones for refresh in Phase 4. Never treat an observation marked inconclusive as negative evidence.
2. **Scan related reports** — invoke `scan-context` with the ticket key, branch, and `{context_dir}`. Exclude results whose `type` is `pr-report` (the skill's own subdirectory) to avoid circular self-reference. Reuse fresh reports as context; record stale reports as ignored.

**Completion criterion:** Fresh prior observations and reports are identified and noted in state; stale ones are flagged for refresh.

## Phase 3: Discover tools

1. **Create skeleton report** — write `{context_dir}/pr-report/{key}-report.md` with section headers and status markers. See [CHECKPOINTING.md](CHECKPOINTING.md).
2. **Discover tools per capability** — for each load-bearing capability (PR metadata, top-level reviews, inline threads, conversation comments, changed files, CI/build, static analysis, issue tracker), invoke `tool-discovery/scripts/discover-tools.py` with the capability name and project `config_dir`. Record the ranked list and the preferred tool in state. See [TOOL_SELECTION.md](TOOL_SELECTION.md). Related context reports are handled in Phase 2a, not here.
3. **Report discovery summary** — note the preferred tool for each capability and any capabilities that are skipped because no tool is available.

**Completion criterion:** The skeleton report exists; the `## Detected Tools` section in state lists a preferred tool for every capability that has one; skipped capabilities are noted with a reason.

## Phase 4: Collect

For each capability, in order of dependency:

1. **Select the preferred tool** for the current capability from the discovery ranking.
2. **Invoke the tool** and collect output. If the tool returns complete data, normalize it into the `pr-adapter-contract` shape via the `normalize-observation` worker, append the result to `chainlog` as an observation (see [CHAINLOG.md](CHAINLOG.md)), write it to the report and state, then move to the next capability.
3. **If the tool returns partial or no data** and a better-ranked tool is available, fall back to the next-best tool and repeat step 2. If the fallback is still degraded, disclose the better tool and apply the configured `pr-report.tooling.degraded_mode` behavior (`ask`, `accept`, or `reject`).
4. **Report progress** after each capability: state the tool used, whether it succeeded, and whether a fallback was taken.
5. **Update the report and checkpoint** after each capability is collected. Invoke `checkpoint/update` to mark the phase, update Current Focus, and identify the next pending capability.

**Capabilities to collect:**

- PR metadata and changed files
- Top-level reviews and inline threads / review comments
- Conversation comments (issue-level PR comments, including bot decorations); classify authors via the `pr-report.bots` config map
- CI / build status
- Static analysis findings
- Issue tracker scope
- Related context reports (collected in Phase 2a via `scan-context`)

**Completion criterion:** Every capability has returned data from the best available tool, or the user/config has explicitly accepted a degraded or skipped source.

## Phase 5: Scope-check and triage

1. **Scope check** — invoke the `scope-checker` block with the scope envelope (resolved per the fallback hierarchy in [REFERENCE.md](REFERENCE.md)), the findings list, and `pr-report.scope_mode` (`strict` or `lenient`) as the strictness parameter.
2. **Triage and synthesize issues** — delegate to `issue-synthesizer`. Group duplicates, challenge every comment, apply source weighting, and produce the issue board.
3. **Generate task list** — if `pr-report.task_list.enabled` is true, generate a list of actionable next steps from the issue board.
4. **Update report and checkpoint** after triage is complete.

**Completion criterion:** Every item is classified as actionable, resolved, outdated, or no-action-needed; the issue board and task list are recorded in the report.

## Phase 6: Report

1. **Render final report** — delegate to `report-writer` to finalize pending Markdown sections.
2. **Optional HTML dashboard** — delegate to `html-renderer` or render the template asset.
3. **Final validation** — invoke `checkpoint/validate` to verify all phases are complete and consistent.
4. **Present findings** — give the user a concise summary with open issues, CI status, data-source disclosures, task list, and a suggested next step.

**Completion criterion:** All report sections are marked `<!-- STATUS: completed -->`, the report frontmatter is updated, `report_status` is `complete`, and the chat summary is delivered.

## Focused mode

In focused mode (`/pr-report ci`, `/pr-report reviews`, `/pr-report static-analysis`, and similar), the workflow narrows but does not change shape:

1. Phase 1 (Initialize) runs fully, but only the requested capability's tooling is validated.
2. Phase 2 (Resolve PR) runs fully.
3. Phase 2a runs only for the requested capability's observations.
4. Phase 3 (Discover tools) runs only for the requested capability.
5. Phase 4 (Collect) collects only the requested capability.
6. Phase 5 (Scope-check and triage) runs on the collected items only.
7. Phase 6 (Report) renders only the requested section, plus **Data sources** and a short summary.

## Fallback-to-better-tool loop

When a tool returns partial or degraded data:

1. Check whether a better-ranked tool was detected for the same capability.
2. If a better tool exists and the user has not disabled fallbacks, invoke it.
3. If the better tool also fails or returns degraded data, stop at the best available tool.
4. Disclose the final tool choice and any better tools that were available.
5. Apply the `pr-report.tooling.degraded_mode` preference:
   - `ask`: stop and ask the user.
   - `accept`: record the degraded source and continue.
   - `reject`: skip the capability and record it as unavailable.

## Manual fallback UX

When no tool is available for a capability or the user explicitly chooses manual input, the conductor asks for the data in steps:

1. **PR metadata** — number, repo, branch, title, body, state.
2. **Changed files** — paste a list or upload a CSV/JSON/Markdown file.
3. **Open comments / review threads** — paste or upload a file.
4. **CI status and static-analysis findings** — include only if the user wants them.
5. **Confirm "no more data"** and proceed to triage.

Supported formats: Markdown with frontmatter, CSV with standard columns, JSON matching the internal shape.

## References

- [TOOL_SELECTION.md](TOOL_SELECTION.md) — capability-to-tool mapping and degradation rules
- [CHAINLOG.md](CHAINLOG.md) — chainlog classification, produced/consumed capabilities, and storage
- [CHECKPOINTING.md](CHECKPOINTING.md) — incremental output and resumption
- [REFERENCE.md](REFERENCE.md) — state spec, report schema, and delta rules
- [CONFIG_PATTERN.md](CONFIG_PATTERN.md) — config schema and first-run flow
- [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md) — produced report schemas
- [VERSIONING.md](VERSIONING.md) — versioning and migration
- [COMMENT_TRIAGE.md](COMMENT_TRIAGE.md) — source weighting and challenge rules
