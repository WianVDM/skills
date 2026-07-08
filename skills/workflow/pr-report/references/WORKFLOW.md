# PR Report Workflow

This is the detailed step sequence that the `pr-report` skill follows. It is a concrete breakdown of the high-level phases described in `SKILL.md`.

## Phase 1: Resolve PR and load context

1. **Load config and state** — read `{config_dir}/pr-report.yaml`, `{config_dir}/shared.yaml`, and `{context_dir}/pr-report/{key}/state.md` if they exist. `{config_dir}` and `{context_dir}` are discovered by `detect-project-context`.
2. **Resolve PR** — identify PR number, repo, branch, and ticket key.
3. **Validate PR capability** — ensure at least one PR source tool is available and its token resolves. If no tool is detected, stop and consult the user.

**Completion criterion:** `pr_number`, `repo`, `branch`, and `key` are recorded in state; the PR capability has a selected tool.

## Phase 2: Create skeleton and discover tools

4. **Create skeleton report** — write `{context_dir}/pr-report/{key}-report.md` with section headers and status markers. See [CHECKPOINTING.md](CHECKPOINTING.md).
5. **Discover tools per capability** — for each load-bearing capability (PR metadata, top-level reviews, inline threads, changed files, CI/build, static analysis, issue tracker, notification feedback, related context reports), detect available tools across all categories (skill adapters, MCP tools, native binaries, direct APIs, harness tools, manual fallback). Rank them and record the preferred tool in state. See [TOOL_SELECTION.md](TOOL_SELECTION.md).
6. **Report discovery summary** — note the preferred tool for each capability and any capabilities that are skipped because no tool is available.

**Completion criterion:** The skeleton report exists; the `## Detected Tools` section in state lists a preferred tool for every capability that has one; skipped capabilities are noted with a reason.

## Phase 3: Collect data

For each capability, in order of dependency:

7. **Select the preferred tool** for the current capability from the discovery ranking.
8. **Invoke the tool** and collect normalized output. If the tool returns `complete` data, write it to the report and state, then move to the next capability.
9. **If the tool returns partial or no data** and a better-ranked tool is available, fall back to the next-best tool and repeat step 8. If the fallback is still degraded, disclose the better tool and apply the configured `tooling.degraded_mode` behavior (`ask`, `accept`, or `reject`).
10. **Update the report and checkpoint** after each capability is collected. Call `checkpoint-manager` to mark the phase, update `Current Focus`, and identify the next pending capability.

**Capabilities to collect:**

- PR metadata and changed files
- Top-level reviews and inline threads / review comments
- CI / build status
- Static analysis findings
- Issue tracker scope
- Notification feedback
- Related context reports (via `context-scout`)

**Completion criterion:** Every capability has returned data from the best available tool, or the user/config has explicitly accepted a degraded or skipped source.

## Phase 4: Triage and synthesize

11. **Scope check** — delegate to `scope-checker`. Compare feedback to the ticket or PR description.
12. **Triage and synthesize issues** — delegate to `issue-synthesizer`. Group duplicates, challenge every comment, apply source weighting, and produce the issue board.
13. **Update report and checkpoint** after triage is complete.

**Completion criterion:** Every item is classified as actionable, resolved, outdated, or no-action-needed; the issue board is recorded in the report.

## Phase 5: Render and finalize

14. **Render final report** — delegate to `report-writer` to finalize pending Markdown sections.
15. **Optional HTML dashboard** — delegate to `html-renderer` or render the template asset.
16. **Final validation** — ask `checkpoint-manager` to verify all phases are complete and consistent.
17. **Present findings** — give the user a concise summary with open issues, CI status, data-source disclosures, and a suggested next step.

**Completion criterion:** All report sections are marked `<!-- STATUS: completed -->`, the report frontmatter is updated, `report_status` is `complete`, and the chat summary is delivered.

## Fallback-to-better-tool loop

When a tool returns partial or degraded data:

1. Check whether a better-ranked tool was detected for the same capability.
2. If a better tool exists and the user has not disabled fallbacks, invoke it.
3. If the better tool also fails or returns degraded data, stop at the best available tool.
4. Disclose the final tool choice and any better tools that were available.
5. Apply the `tooling.degraded_mode` preference:
   - `ask`: stop and ask the user.
   - `accept`: record the degraded source and continue.
   - `reject`: skip the capability and record it as unavailable.

## References

- [TOOL_SELECTION.md](TOOL_SELECTION.md) — capability-to-tool mapping and degradation rules
- [CHECKPOINTING.md](CHECKPOINTING.md) — incremental output and resumption
- [ADAPTER_ARCHITECTURE.md](ADAPTER_ARCHITECTURE.md) — adapter taxonomy and contract
- [CAPABILITIES.md](CAPABILITIES.md) — capability detection and lazy loading
- [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md) — produced report schemas
- [REFERENCE.md](REFERENCE.md) — state spec, report schema, and delta rules
- [CONFIG_PATTERN.md](CONFIG_PATTERN.md) — config schema and first-run flow
