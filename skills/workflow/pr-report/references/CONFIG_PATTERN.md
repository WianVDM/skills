# Configuration and Notes

`pr-report` uses the config + notes pattern. It detects the environment, asks for missing information once, persists the answers, and reuses them on future runs.

## Canonical location

Config and notes live in the detected project configuration directory:

```text
{config_dir}/pr-report.yaml
```

`{config_dir}` is discovered by the `detect-project-context` building block. The default is `{project-root}/.agents/config`, but the skill does not assume that path. See [Initialization](../SKILL.md#initialization) in `SKILL.md` for the detection routine.

Reports and state live in the detected project context directory:

```text
{context_dir}/pr-report/
```

`{context_dir}` is also discovered by `detect-project-context`. The default is `{project-root}/.agents/context`.

## First-run flow

1. **Load existing config** — read `{config_dir}/pr-report.yaml` if it exists.
2. **Detect project context** — use `detect-project-context` to find `{project-root}`, `{config_dir}`, and `{context_dir}`.
3. **Detect environment** — inspect git remote, environment variables, and configured MCP config sources for adapter tokens and endpoints.
4. **Ask only for missing values** — required: PR source adapter. Optional: CI, static-analysis, issue-tracker, and notification adapters.
5. **Persist** — write the resolved config to `{config_dir}/pr-report.yaml`.
6. **Continue** — use the newly created config.

## Adapter detection

Provider detection is the default behavior. When an adapter setting is `auto`, the skill selects an adapter by inspecting, in order:

- The configured `adapters.{role}.source` value.
- Available MCP servers and environment variables.
- The git remote.
- Project files such as CI configuration.

The skill does not assume a specific harness, model, or tool. It uses the adapter registry documented in `references/ADAPTER_ARCHITECTURE.md` to map `source` names to adapter implementations.

### Token resolution

Adapters receive tokens through a shared `token-resolver` building block. Tokens are resolved in this order:

1. Literal value in `adapters.{role}.config.token`.
2. `${ENV_VAR}` reference in `adapters.{role}.config.token`.
3. Valid token extracted from configured MCP config.
4. Ask the user once, then persist the env-var name or secure reference to config.

Tokens are never written in plain text to report or state files.

## Legacy fallback

For backward compatibility, the skill may read existing user-level config files on first run:

- `$PR_REPORT_CONFIG`
- `$XDG_CONFIG_HOME/pr-report/config.yml`
- `~/.config/pr-report/config.yml`
- `~/.pr-report/config.yml`

The skill does not write updates back to these legacy paths. Once migrated, `{config_dir}/pr-report.yaml` is the source of truth.

## Config schema

```yaml
# Shared keys (resolved by detect-project-context, stored in {config_dir}/shared.yaml)
agents:
  context_dir: .agents/context
  config_dir: .agents/config

# Skill-specific keys (stored in {config_dir}/pr-report.yaml)
adapters:
  pr:
    source: github-pr-adapter      # auto | github-pr-adapter | gitlab-pr-adapter | manual-pr-adapter | ...
    config:
      repo: owner/repo
      token: ${GITHUB_TOKEN}
  ci:
    source: github-actions-adapter # auto | github-actions-adapter | azure-pipelines-adapter | none | ...
    config:
      token: ${GITHUB_TOKEN}
  static_analysis:
    source: sonarcloud-adapter     # auto | sonarcloud-adapter | sonarqube-adapter | codeql-adapter | none | ...
    config:
      organization: my-org
      project_key: my-org_repo
      token: ${SONAR_TOKEN}
  issue_tracker:
    source: jira-adapter           # auto | jira-adapter | linear-adapter | github-issues-adapter | none | ...
    config:
      base_url: https://my-org.atlassian.net
      token: ${JIRA_TOKEN}
  notification:
    sources: []                    # [teams-adapter, slack-adapter, ...]

bots:
  sonarqube:
    usernames: [sonarqubecloud]
    source_type: static_analysis
    default_severity: required
  coderabbit:
    usernames: [coderabbitai, coderabbit[bot]]
    source_type: automated_reviewer
    default_severity: recommended
  tate:
    usernames: [T876]
    source_type: hybrid_reviewer
    default_severity: required_to_resolve

notes: []
```

See `references/ADAPTER_ARCHITECTURE.md` for the adapter interface and registry format.

## Self-updates

The skill may append to `notes` and update non-secret fields in place:

- Detected project context directory and source.
- Adapter URLs and organizations discovered from MCP config.
- Adapter availability/unavailability observations.
- User preference explanations.

Rules:

- **Append-only for notes.** Never delete observations.
- **Do not overwrite user values silently.** If auto-discovery conflicts with an explicit config value, report the conflict and ask.
- **Do not log tokens.** Tokens are referenced by env var names or stored securely; never written into report or state files.
- **Timestamp observations.** Each note should include an ISO date.

## User consultation

When an adapter cannot be resolved or its token is missing, explain what was already tried and present options:

1. Paste a token.
2. Provide an environment variable name.
3. Say `skip` to skip this adapter this run.
4. Say `disable` to turn off this adapter permanently.
