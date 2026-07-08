---
name: pr-report-tool-selection
description: Capability-to-tool mapping for the pr-report conductor. Defines how each load-bearing capability is fulfilled by the best available tool, with fallback sources and degradation disclosure.
metadata:
  author: Wian van der Merwe
  tags: [pr-report, tooling, capabilities, tool-selection]
  version: "1.0.0"
---

# Tool Selection

`pr-report` is capability-first. For every load-bearing capability it needs, it discovers the available tools, selects the one that returns the most complete and authoritative data, and falls back to the next-best tool when the preferred tool is unavailable or partial.

Adapters are one implementation strategy among many. The conductor also considers MCP tools/servers, native binaries, direct provider APIs, harness tools, and manual fallback.

## Capability matrix

| Capability | Best source | Fallback sources | Manual fallback |
|---|---|---|---|
| PR metadata (title, body, author, state) | GitHub MCP / API or `github-pr-adapter` | `manual-pr-adapter`, user input | User-provided summary |
| Changed files | `github-pr-adapter` or GitHub MCP | Git CLI (`git diff`), manual entry | User-provided file list |
| Top-level reviews | `github_get_pull_request_reviews` (MCP) | `github-pr-adapter`, `manual-pr-adapter` | User-provided review text |
| Inline threads / review comments | `github-pr-adapter` or GitHub MCP | `manual-pr-adapter` | User-provided thread text |
| CI / build status | GitHub Checks MCP or `github-actions-adapter` | commit-status API, `manual-pr-adapter` | User-provided CI summary |
| Static analysis findings | SonarQube/SonarCloud MCP or API | `sonarcloud-adapter`, `manual-pr-adapter` | User-provided findings CSV |
| Issue tracker scope | Jira MCP / API or `jira-adapter` | `manual-pr-adapter`, PR description | User-provided scope text |
| Notification feedback | Teams/Slack MCP or API | `teams-adapter`, `slack-adapter`, `manual-pr-adapter` | User-provided notes |
| Related context reports | `context-scout` subagent | Direct file scan of `{context_dir}` | None — skip if absent |

## Tool categories

The conductor considers tools in this order when discovering candidates for a capability:

1. **Skill adapters** — pluggable skills such as `github-pr-adapter`, `sonarcloud-adapter`, `jira-adapter`.
2. **MCP tools / servers** — tools exposed through the MCP gateway, such as `github_get_pull_request_reviews` or a SonarQube MCP server.
3. **Native binaries** — CLI tools such as `gh`, `git`, `curl`, `jq`.
4. **Direct APIs** — provider REST or GraphQL endpoints called directly.
5. **Harness tools** — built-in browser, file system, search, or shell capabilities.
6. **Manual fallback** — user input, CSV, or markdown files.

## Tool discovery rules

For every capability, the conductor performs the following discovery steps:

1. **Read config** — inspect `.agents/config/pr-report.yaml` for explicit per-capability tool preferences (`tooling.preference` and `adapters.{role}.source`).
2. **Read MCP config** — list configured MCP servers from `.mcp.json` and query the MCP gateway for available tools.
3. **Check adapter registry** — inspect the built-in and project-registered adapter skills from `references/ADAPTER_REGISTRY.md`.
4. **Check native binaries** — verify whether relevant binaries (`gh`, `git`, `curl`) are available in the environment.
5. **Record detected tools** — write the ranked list per capability to `{context_dir}/pr-report/{key}/state.md` under `## Detected Tools`.

If a capability has no detected tool and the user preference is not `reject`, record the capability as skipped and note it in the report.

## Selection hierarchy

When ranking detected tools for a capability, prefer the tool that:

1. Returns the most complete, authoritative, and reliable data for the capability.
2. Is already configured and working (token resolves, endpoint reachable).
3. Requires no additional user setup.
4. Returns direct evidence rather than reconstructed or inferred data.
5. Falls back to skill adapters only when they are the best or only option.

The user's explicit preference in `tooling.preference` overrides the automatic ranking. The ranking is recorded in state so that the fallback order is transparent and reproducible.

## Degradation behavior

When only a degraded source is available for a capability, the conductor behaves according to the `tooling.degraded_mode` config key:

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

## Out of scope

- This file does not define the normalized adapter interface. See `pr-adapter-contract` for that.
- This file does not define the config schema. See `references/CONFIG_PATTERN.md` for that.
- This file does not define the report schema. See `references/CONTEXT_REPORTS.md` for that.

## References

- `pr-adapter-contract` — normalized adapter interface
- `token-resolver` — secure token resolution
- `context-reports` — context report format
- [ADAPTER_ARCHITECTURE.md](ADAPTER_ARCHITECTURE.md) — adapter taxonomy and interface contract
- [ADAPTER_REGISTRY.md](ADAPTER_REGISTRY.md) — default adapter registry
- [CAPABILITIES.md](CAPABILITIES.md) — capability detection and lazy loading
- [CONFIG_PATTERN.md](CONFIG_PATTERN.md) — config schema and first-run flow
- [WORKFLOW.md](WORKFLOW.md) — detailed workflow steps
