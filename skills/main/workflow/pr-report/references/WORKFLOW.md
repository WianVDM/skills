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

- **Multiple PRs matching a ticket key** — after `identity-resolver` returns `type: ticket`, search open PRs for a matching title or branch. Ask the user to pick one, or use the most recently updated one if confidence is medium.
- **No open PR for the current branch** — stop and ask the user to create a PR or provide a number.
- **PR URL provided** — `identity-resolver` parses `owner/repo/pull/number` from the URL and returns it directly.
- **Forks** — detect the base repo from the upstream remote or the PR head repo from the PR URL.
- **Ambiguous repo** — if `git remote` has multiple entries, ask the user to select one and persist the choice.

## Phase 3: Discover tools

1. **Create skeleton report** — write `{context_dir}/pr-report/{key}-report.md` with section headers and status markers. See [CHECKPOINTING.md](CHECKPOINTING.md).
2. **Discover tools per capability** — for each load-bearing capability (PR metadata, top-level reviews, inline threads, changed files, CI/build, static analysis, issue tracker, related context reports), invoke `tool-discovery/scripts/discover-tools.py` with the capability name and project `config_dir`. Record the ranked list and the preferred tool in state. See [TOOL_SELECTION.md](TOOL_SELECTION.md).
3. **Report discovery summary** — note the preferred tool for each capability and any capabilities that are skipped because no tool is available.

**Completion criterion:** The skeleton report exists; the `## Detected Tools` section in state lists a preferred tool for every capability that has one; skipped capabilities are noted with a reason.

## Phase 4: Collect

For each capability, in order of dependency:

1. **Select the preferred tool** for the current capability from the discovery ranking.
2. **Invoke the tool** and collect output. If the tool returns complete data, normalize it into the internal model and write it to the report and state, then move to the next capability.
3. **If the tool returns partial or no data** and a better-ranked tool is available, fall back to the next-best tool and repeat step 2. If the fallback is still degraded, disclose the better tool and apply the configured `pr-report.tooling.degraded_mode` behavior (`ask`, `accept`, or `reject`).
4. **Report progress** after each capability: state the tool used, whether it succeeded, and whether a fallback was taken.
5. **Update the report and checkpoint** after each capability is collected. Call `checkpoint-manager` to mark the phase, update `Current Focus`, and identify the next pending capability.

**Capabilities to collect:**

- PR metadata and changed files
- Top-level reviews and inline threads / review comments
- CI / build status
- Static analysis findings
- Issue tracker scope
- Related context reports (via `context-scout`)

**Completion criterion:** Every capability has returned data from the best available tool, or the user/config has explicitly accepted a degraded or skipped source.

## Phase 5: Scope-check and triage

1. **Scope check** — delegate to `scope-checker`. Compare feedback to the ticket or PR description.
2. **Triage and synthesize issues** — delegate to `issue-synthesizer`. Group duplicates, challenge every comment, apply source weighting, and produce the issue board.
3. **Generate task list** — if `pr-report.task_list.enabled` is true, generate a list of actionable next steps from the issue board.
4. **Update report and checkpoint** after triage is complete.

**Completion criterion:** Every item is classified as actionable, resolved, outdated, or no-action-needed; the issue board and task list are recorded in the report.

## Phase 6: Report

1. **Render final report** — delegate to `report-writer` to finalize pending Markdown sections.
2. **Optional HTML dashboard** — delegate to `html-renderer` or render the template asset.
3. **Final validation** — ask `checkpoint-manager` to verify all phases are complete and consistent.
4. **Present findings** — give the user a concise summary with open issues, CI status, data-source disclosures, task list, and a suggested next step.

**Completion criterion:** All report sections are marked `<!-- STATUS: completed -->`, the report frontmatter is updated, `report_status` is `complete`, and the chat summary is delivered.

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
- [CHECKPOINTING.md](CHECKPOINTING.md) — incremental output and resumption
- [REFERENCE.md](REFERENCE.md) — state spec, report schema, and delta rules
- [CONFIG_PATTERN.md](CONFIG_PATTERN.md) — config schema and first-run flow
- [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md) — produced report schemas
- [VERSIONING.md](VERSIONING.md) — versioning and migration
- [COMMENT_TRIAGE.md](COMMENT_TRIAGE.md) — source weighting and challenge rules
