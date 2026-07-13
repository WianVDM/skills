# Tool Selection

`pr-report` is capability-first. For every load-bearing capability it needs, it discovers the available tools, selects the one that returns the most complete and authoritative data, and falls back to the next-best tool when the preferred tool is unavailable or partial.

The conductor considers MCP tools/servers, native binaries, direct provider APIs, harness tools, and manual fallback for every capability. No single tool category is treated as the default.

## Capability matrix

| Capability | Best tools | Fallback tools | Manual fallback |
|---|---|---|---|
| PR metadata | GitHub MCP, `gh` CLI | GitHub REST API, `git` remote heuristics | User-provided summary |
| Changed files | GitHub MCP, `gh` CLI | `git diff` against base branch | User-provided file list |
| Top-level reviews | GitHub MCP (`github_get_pull_request_reviews`) | `gh` CLI, GitHub REST API | User-provided review text |
| Inline threads | GitHub MCP, `gh` CLI | GitHub REST API | User-provided thread text |
| CI / build status | GitHub MCP (`github_get_check_runs`), `gh` CLI | GitHub Checks API, commit-status API | User-provided CI summary |
| Static analysis | SonarCloud/SonarQube MCP, SonarCloud API | SonarQube API, Semgrep MCP, CodeQL CLI | User-provided findings CSV |
| Issue tracker scope | Jira MCP, Jira API | Linear MCP, GitHub Issues MCP | User-provided scope text |
| Related context reports | Direct file scan of `{context_dir}` | None | Skip if absent |

## Tool categories

The conductor considers tools in this order when discovering candidates for a capability:

1. **MCP tools / servers** — tools exposed through the MCP gateway, such as `github_get_pull_request_reviews`, `github_get_check_runs`, or a SonarQube MCP server.
2. **Native binaries** — CLI tools such as `gh`, `git`, `curl`, `jq`.
3. **Direct APIs** — provider REST or GraphQL endpoints called directly, only when the user has explicitly configured an endpoint and confirmed it.
4. **Harness tools** — built-in browser, file system, search, or shell capabilities.
5. **Manual fallback** — user input, CSV, or markdown files.

## Provider capability matrix

Out-of-box providers are the ones `pr-report` can use without requiring a custom adapter skill. Community or future providers are listed for reference but are not required for this version.

| Capability | Out-of-box providers | Community / future |
|---|---|---|
| PR source | GitHub, manual | GitLab, Bitbucket, Azure DevOps, Gitea |
| CI | GitHub Actions | Azure Pipelines, GitLab CI, Jenkins |
| Static analysis | SonarCloud | SonarQube, CodeQL, Semgrep |
| Issue tracker | Jira | Linear, GitHub Issues, Azure Boards |

Notification feedback is deferred until a concrete MCP server, CLI, or API provider exists; it does not appear in the out-of-box matrix for this version.

## Discovery rules

For every capability, the conductor performs the following discovery steps:

1. **Read config** — inspect `.agents/config/pr-report.yaml` for explicit per-capability tool preferences (`pr-report.tools.{capability}.provider` and `pr-report.tooling.preference`).
2. **Read MCP config** — list configured MCP servers from `.mcp.json` or equivalent harness config, and probe known tool names (`github_get_pull_request_reviews`, `github_get_check_runs`, `sonarcloud_find_issues`, `jira_get_issue`).
3. **Check native binaries** — verify whether relevant binaries (`gh`, `git`, `curl`) are available in the environment.
4. **Check direct API prerequisites** — if a capability has an explicit `endpoint` configured and the user has confirmed it, mark direct API as available.
5. **Record detected tools** — write the ranked list per capability to `{context_dir}/pr-report/{key}/state.md` under `## Detected Tools`.

If the harness does not expose a way to list MCP tools, the conductor discloses that limitation and falls back to native binaries or manual input.

If a capability has no detected tool and the user preference is not `reject`, record the capability as skipped and note it in the report.

## Selection hierarchy

When ranking detected tools for a capability, prefer the tool that:

1. Returns the most complete, authoritative, and reliable data for the capability.
2. Is already configured and working (token resolves, endpoint reachable).
3. Requires no additional user setup.
4. Returns direct evidence rather than reconstructed or inferred data.
5. Fits the skill's contract without leaking implementation details.

The user's explicit preference in `pr-report.tooling.preference` overrides the automatic ranking. The ranking is recorded in state so that the fallback order is transparent and reproducible.

## Conflict resolution

When two available tools return conflicting data for the same capability (e.g., GitHub MCP says CI passed, `gh` CLI says it failed), the conductor:

1. Prefers the more authoritative source (MCP or CLI over inferred data).
2. Records the conflict in the report's **Data sources** section.
3. If the conflict affects a blocking item, asks the user which source to trust.
4. Never silently synthesizes a single answer from conflicting sources.

## Timeout and retry policy

External tool calls follow this resilience policy:

- Retry once on transient network errors (5xx, timeout).
- Time out after a configurable duration (default 30 seconds per call).
- On timeout or persistent failure, fall back to the next-best tool or mark the capability degraded.
- Record timeouts and retries in the **Data sources** section.

## Direct API call policy

Direct HTTP API calls are a last resort and are only allowed when:

1. The user has explicitly configured an endpoint in `pr-report.tools.{capability}.endpoint`.
2. The user has confirmed the endpoint and token for this run, or the confirmation is persisted in config notes.
3. The skill discloses that it is using a direct API call and records the provider in the **Data sources** section.

Direct API calls are not automatic. If the user declines, fall back to manual input.

## Degradation behavior

When only a degraded source is available for a capability, the conductor behaves according to the `pr-report.tooling.degraded_mode` config key:

| Mode | Behavior |
|---|---|
| `ask` | Stop and ask the user whether to use the better tool, accept the degraded source, or skip the capability. This is the default. |
| `accept` | Proceed with the degraded source and record the disclosure in the report. |
| `reject` | Skip the capability and record it as unavailable. |

## Degradation disclosure template

When a degraded source is used, include a paragraph in the report and in the chat summary:

> I used `{tool}` for `{capability}` because `{reason}`. A better source, `{better_tool}`, is configured and available. If you want me to fetch from `{better_tool}` instead, confirm and I will rerun that section. Otherwise the current section may be degraded.

When the degraded source is accepted silently (`accept` mode), still include a short note in the report's **Data sources** section:

> `{capability}`: `{tool}` (degraded; `{better_tool}` was available).

## Data sources section

The final report must include a **Data sources** section that lists, for each capability:

- The tool used.
- The alternative tools detected.
- Any degraded sources accepted by the user or config.
- The confidence assigned to the data from that source.

This section makes the tool-selection process transparent and auditable.

## Lazy loading

The conductor evaluates recommended and optional tooling only when the branch that needs it is selected. For example, static-analysis configuration is only checked when the user asks for a full report or explicitly includes static analysis. The initialization phase checks only the required PR source capability.

## Out of scope

- This file does not define the internal normalization model. See `references/REFERENCE.md` for that.
- This file does not define the config schema. See `references/CONFIG_PATTERN.md` for that.
- This file does not define the report schema. See `references/CONTEXT_REPORTS.md` for that.

## References

- `token-resolver` — secure token resolution
- `context-reports` — context report format
- `worker-contract` — shared subagent return format
- [CONFIG_PATTERN.md](CONFIG_PATTERN.md) — config schema and first-run flow
- [WORKFLOW.md](WORKFLOW.md) — detailed workflow steps
- [REFERENCE.md](REFERENCE.md) — internal normalization model and state schema
