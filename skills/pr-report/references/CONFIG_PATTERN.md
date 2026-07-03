# Configuration and Notes

`pr-report` uses the config + notes pattern. It detects the environment, asks for missing information once, persists the answers, and reuses them on future runs.

## Canonical location

```text
{project-root}/.agents/config/pr-report.yaml
```

## First-run flow

1. **Load existing config** — read `.agents/config/pr-report.yaml` if it exists.
2. **Detect environment** — inspect environment variables and configured MCP config paths for provider tokens and endpoints. See [Harness and provider detection](#harness-and-provider-detection).
3. **Ask only for missing values** — PR platform, CI provider, static analysis, issue tracker, artifact directory.
4. **Persist** — write the resolved config to `.agents/config/pr-report.yaml`.
5. **Continue** — use the newly created config.

## Harness and provider detection

The skill does not assume a specific harness, model, or tool. Detection is the default behavior.

- **Harness detection.** When `harness` is `auto`, the skill checks environment variables and the configured `mcp_config_sources` to determine which harness or MCP setup is present. It does not rely on a hardcoded list of harness names.
- **Provider detection.** When a provider setting is `auto`, the skill selects an adapter by inspecting:
  - configured tokens and endpoints,
  - available MCP servers,
  - the git remote,
  - project files such as CI configuration.
- **MCP config paths.** Paths in `mcp_config_sources` are user-configured examples, not defaults. The skill also checks common environment variables such as `MCP_CONFIG_PATH`, `CLAUDE_MCP_CONFIG`, `KIMI_MCP_CONFIG`, and `GEMINI_MCP_CONFIG` when present. Configure only the paths that match your environment.

## Legacy fallback

For backward compatibility, the skill may read existing user-level config files on first run:

- `$PR_REPORT_CONFIG`
- `$XDG_CONFIG_HOME/pr-report/config.yml`
- `~/.config/pr-report/config.yml`
- `~/.pr-report/config.yml`

The skill does not write updates back to these legacy paths. Once migrated, the project-level config is the source of truth.

## Self-updates

The skill may append to `notes` and update non-secret fields in place:

- Detected harness and MCP config source.
- Provider URLs and organizations discovered from MCP config.
- That GraphQL or a specific provider is available/unavailable.
- User preference explanations.

Rules:

- **Append-only for notes.** Never delete observations.
- **Do not overwrite user values silently.** If auto-discovery conflicts with an explicit config value, report the conflict and ask.
- **Do not log tokens.** Tokens are referenced by env var names or stored securely; never written into report or state files.
- **Do not hardcode harness names.** Detection must rely on env vars and configured paths, not a fixed list of harnesses.
- **Timestamp observations.** Each note should include an ISO date.

## Token resolution

For each provider, use the first available source in this order:

1. Literal value in `tokens.{provider}`.
2. `${ENV_VAR}` reference in `tokens.{provider}`.
3. Valid token extracted from detected MCP config.
4. Ask the user once, then save the env-var name or secure reference to config.

## User consultation

When a token cannot be resolved, explain what was already tried and present options:

1. Paste a token.
2. Provide an environment variable name.
3. Say `skip` to skip this provider this run.
4. Say `disable` to turn off this provider permanently.
