# Dependencies

## Required skills

- `checkpoint` — maintains phase state and resume state.
- `research-ticket` — fetches and normalizes ticket data.
- `map-ticket-relationships` — enriches raw tracker references into a relationship graph.
- `explore-code` — searches the codebase for evidence when the ticket is code-related.
- `challenge-assumptions` — stress-tests assumptions for confirmation bias.
- `scan-context` — discovers related context reports.
- `context-reports` — shared conventions for report schemas and freshness.
- `worker-contract` — shared subagent return format and scope boundaries.

## Recommended skills

- `baseline` — captures ground-truth evidence for verifiable tickets. Used only when `detect-verifiable-state` returns `verifiable: true` and `baseline_mode` is not `skip`. Without it, the conductor reports degraded baseline capability.

## Required tools

- `read` — inspect context, config, and reports.
- `write` — write reports and state files.
- `edit` — update checkpoint state and incremental report sections.
- `bash` — run deterministic helper scripts and git commands.

## Recommended tools

- `mcp` — invoke tracker MCP servers when configured. If unavailable, the skill falls back to REST APIs via `bash` and env vars.
- `ffgrep` — search file contents when `explore-code` uses harness tools.
- `fffind` — discover files when `explore-code` uses harness tools.

## Required binaries

- `git` — used by `get-git-state` and relationship-mapping scripts.
- `python3` — used by all deterministic helper scripts.

## Required environment variables

Variables are referenced by name in `debrief.yaml`, not hardcoded. The exact variables depend on the configured tracker:

- Jira: `JIRA_API_TOKEN`, `JIRA_USERNAME` (optional), `JIRA_SERVER_URL`.
- GitHub: `GITHUB_TOKEN`.
- Linear: `LINEAR_API_TOKEN`.

## Required scripts

- `load-skill-config` — load and merge project config.
- `detect-issue-tracker` — detect available issue trackers.
- `extract-ticket-key` — resolve ticket key from input or branch.
- `get-git-state` — detect current branch, commit, and remote.
- `resolve-tracker-credentials` — resolve env-var credentials.
- `detect-verifiable-state` — decide whether `baseline` is relevant.
- `calculate-confidence` — calculate confidence score from assumptions and contradictions.
- `check-debrief-freshness` — decide whether to reuse an existing report.
- `_frontmatter` — shared frontmatter parser.

## Recommended scripts

- `find-related-prs` — discover PRs/branches/commits related to a ticket. Used by `map-ticket-relationships` when available.
- `trace-bug-origin` — trace original feature or regression commit for bug tickets. Used by `map-ticket-relationships` when available.

## Optional scripts

- None.

## Capability-to-tool strategy

| Capability | Preferred tool | Fallback | Selection rule | Degradation disclosure |
|---|---|---|---|---|
| Ticket data fetching | Tracker MCP server via `mcp` | REST API via `bash` + env vars | Use `detect-issue-tracker` to find the best available tracker adapter; prefer MCP if configured. | Tell the user when MCP is unavailable and REST is used. |
| Relationship mapping | `map-ticket-relationships` skill | Inline analysis by conductor | Always use the skill unless it is unavailable, in which case the conductor performs minimal inline mapping. | Note degraded relationship depth. |
| Codebase evidence | Harness search tools (`ffgrep`, `fffind`, `read`) | `bash` + `rg` | Use harness tools first; fall back to `bash`/`rg` only if harness search is insufficient. | Tell the user when `rg` fallback is used. |
| State / resume | `checkpoint` skill | None | Required. If missing, fail closed. | Block. |
| Baseline capture | `baseline` skill | Manual observation recorded by user | Use `baseline` if verifiable and `baseline_mode` != `skip`; otherwise ask the user to describe observable state. | Tell the user baseline is skipped and why. |
| Confidence calculation | `calculate-confidence` script | None | Required. If missing, fail closed. | Block. |
| Report freshness | `check-debrief-freshness` script | None | Required. If missing, fail closed. | Block. |

## Consumed context reports

- Baseline reports from `baseline`.
- Handoff reports from `handoff` / other conductors.
- Prior debriefs from `debrief`.

## Produced context reports

- Debrief reports in `{context_dir}/debrief/{key}-{slug}.md`.
- Checkpoint state in `{context_dir}/debrief/{key}/state.md`.
