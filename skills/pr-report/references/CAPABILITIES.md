# Capability Detection

`pr-report` discovers which providers are available and chooses the right adapter for each. It never assumes a specific harness or tool. Provider detection is the default behavior; explicit configuration overrides detection.

## Detected capabilities

| Capability | Adapters | Detection method |
|------------|----------|------------------|
| PR platform | GitHub, Azure DevOps, GitLab, Bitbucket, manual | Configured `pr_provider`; MCP server availability; git remote. |
| CI / build | GitHub Actions, Azure Pipelines, GitLab CI, Jenkins, none | Configured `ci.provider`; MCP server availability; PR platform. |
| Static analysis | SonarCloud, SonarQube, CodeQL, Semgrep, none | Configured `static_analysis.provider`; MCP server availability; tokens. |
| Issue tracker | Jira, GitHub, Linear, none | Configured `issue_tracker.provider`; MCP server availability; tokens. |

## Harness detection

1. Read `harness` from config.
2. If `auto`, inspect environment variables and the configured `mcp_config_sources` in order.
3. Detect an available harness by checking which configured MCP config paths exist, parse, and contain usable `mcpServers`. The skill does not assume or hardcode harness names such as `kimi`, `claude`, `gemini`, or `vscode`; it relies on file contents and env vars such as `MCP_CONFIG_PATH`, `CLAUDE_MCP_CONFIG`, `KIMI_MCP_CONFIG`, `GEMINI_MCP_CONFIG`, and `VSCODE_MCP_CONFIG`.
4. Write the detected harness source to `notes` using a descriptive label, not a vendor name, unless the user configured one.

## Token extraction

For the detected MCP config, parse `mcpServers` and inspect each server's `env` block:

| Provider | Token keys searched |
|---|---|
| GitHub | `GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_TOKEN` |
| SonarCloud/SonarQube | `SONARQUBE_TOKEN`, `SONAR_TOKEN`, `SONARCLOUD_TOKEN` |
| Jira | `JIRA_API_TOKEN`, `JIRA_TOKEN` |

Also extract provider URLs and organizations when present.

## Token validation

Test each extracted token with a lightweight call before trusting it:

| Provider | Validation call |
|---|---|
| GitHub | Authenticated call to the GraphQL viewer endpoint or equivalent. |
| SonarCloud | Lightweight component lookup for the configured project. |
| Jira | Lightweight authenticated user lookup. |

If validation fails, try the next source. If all sources fail, consult the user.

## Graceful degradation

Distinguish **missing/disabled** resources from **connection failures**.

| Situation | Behavior |
|-----------|----------|
| Provider not configured or MCP missing | Report plainly and continue without that source. |
| Provider configured but connection fails | Stop and consult the user. |

Always include a one-line note in the report when a source is skipped because it is missing or disabled.
