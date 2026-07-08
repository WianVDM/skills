# Capability Detection

`pr-report` discovers which adapters are available and chooses the right one for each role. It never assumes a specific harness or tool. Adapter detection is the default behavior; explicit configuration overrides detection.

Adapter roles and available implementations are defined in `references/ADAPTER_ARCHITECTURE.md`. The conductor loads only the adapters needed for the current run, using lazy dependency evaluation.

## Detected capabilities

| Adapter role | Built-in adapters | Detection method |
|---|---|---|
| PR source | `github-pr-adapter`, `manual-pr-adapter` | Configured `adapters.pr.source`; git remote; user input. |
| CI / build | `github-actions-adapter` | Configured `adapters.ci.source`; MCP server availability; PR source. |
| Static analysis | `sonarcloud-adapter` | Configured `adapters.static_analysis.source`; MCP server availability; tokens. |
| Issue tracker | `jira-adapter` | Configured `adapters.issue_tracker.source`; MCP server availability; tokens. |
| Notification | `teams-adapter`, `slack-adapter` (community) | Configured `adapters.notification.sources`. |

Community adapters for GitLab, Gitea, Azure DevOps, Bitbucket, SonarQube, CodeQL, Semgrep, Linear, and others are documented in the adapter registry.

## Adapter discovery

1. Read `adapters.{role}.source` from config.
2. If `auto`, inspect the git remote and configured MCP config sources to suggest a default adapter.
3. If the adapter is missing or disabled, report plainly and continue without that source.
4. If the adapter is configured but fails to connect, stop and consult the user.

Adapter detection does not rely on hardcoded harness names or tool paths. It uses the shared `detect-project-context` and `token-resolver` building blocks.

## Token resolution

Token resolution is delegated to the `token-resolver` building block. See `references/CONFIG_PATTERN.md` for the resolution order and security rules.

## Graceful degradation

Distinguish **missing/disabled** adapters from **connection failures**.

| Situation | Behavior |
|-----------|----------|
| Adapter not configured or unavailable | Report plainly and continue without that source. |
| Adapter configured but connection fails | Stop and consult the user. |

Always include a one-line note in the report when a source is skipped because it is missing or disabled.
