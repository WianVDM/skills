# Capability Detection

`pr-report` discovers which tools are available for each capability and chooses the best one. It never assumes a specific harness or tool. Adapters are one source among skill adapters, MCP tools/servers, native binaries, direct APIs, harness tools, and manual fallback.

Tool roles and available implementations are defined in [TOOL_SELECTION.md](TOOL_SELECTION.md). The conductor loads only the tools needed for the current run, using lazy dependency evaluation.

## Detected capabilities

| Capability | Built-in tools | Detection method |
|---|---|---|
| PR source | `github-pr-adapter`, `manual-pr-adapter`, GitHub MCP, `gh` CLI | Configured `adapters.pr.source`; MCP server availability; git remote; user input. |
| CI / build | `github-actions-adapter`, GitHub Checks MCP, commit-status API | Configured `adapters.ci.source`; MCP server availability; PR source. |
| Static analysis | `sonarcloud-adapter`, SonarQube/SonarCloud MCP | Configured `adapters.static_analysis.source`; MCP server availability; tokens. |
| Issue tracker | `jira-adapter`, Jira MCP | Configured `adapters.issue_tracker.source`; MCP server availability; tokens. |
| Notification | `teams-adapter`, `slack-adapter` (community), Teams/Slack MCP | Configured `adapters.notification.sources`. |

Community adapters and direct APIs for GitLab, Gitea, Azure DevOps, Bitbucket, SonarQube, CodeQL, Semgrep, Linear, and others are documented in the adapter registry.

## Tool discovery

1. Read `adapters.{role}.source` and `tooling.preference` from config.
2. If `auto` or not configured, inspect all tool categories: configured adapters, MCP servers and tools, native binaries, direct APIs, and manual fallback.
3. If the best available tool is not the configured adapter, disclose it and ask the user whether to switch.
4. If a tool is missing or disabled, report plainly and continue without that source.
5. If a tool is configured but fails to connect, stop and consult the user.

Tool discovery does not rely on hardcoded harness names or tool paths. It uses the shared `detect-project-context` and `token-resolver` building blocks.

The full capability-to-tool mapping and selection hierarchy are in [TOOL_SELECTION.md](TOOL_SELECTION.md).

## Token resolution

Token resolution is delegated to the `token-resolver` building block. See `references/CONFIG_PATTERN.md` for the resolution order and security rules.

## Graceful degradation

Distinguish **missing/disabled** adapters from **connection failures**.

| Situation | Behavior |
|-----------|----------|
| Adapter not configured or unavailable | Report plainly and continue without that source. |
| Adapter configured but connection fails | Stop and consult the user. |

Always include a one-line note in the report when a source is skipped because it is missing or disabled, and note the best available tool if a degraded source is used.
