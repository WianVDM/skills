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

See the `## Initialization` section in `SKILL.md` for the first-run sequence. The summary is:

1. Load existing config.
2. Detect project context and environment.
3. Ask only for missing values.
4. Persist resolved config.
5. Continue using the new config.

## Adapter and tool detection

Provider detection is the default behavior. When an adapter setting is `auto`, the skill selects the best tool for the capability by inspecting, in order:

- Explicit per-capability tool preferences (`tooling.preference`).
- The configured `adapters.{role}.source` value.
- Available MCP servers and tools.
- Native binaries (`gh`, `git`, `curl`, etc.).
- Direct APIs and environment variables.
- The git remote and project files such as CI configuration.

The skill does not assume a specific harness, model, or tool. It uses the capability-to-tool mapping in `references/TOOL_SELECTION.md` and the adapter registry in `references/ADAPTER_ARCHITECTURE.md` to map `source` names to implementations.

### Tooling preference and degraded mode

Two config keys control tool selection behavior globally:

- `tooling.preference` — `auto` selects the best available tool; `adapters` prefers skill adapters; `mcp` prefers MCP tools; `manual` always asks.
- `tooling.degraded_mode` — `ask` prompts the user before accepting a degraded source; `accept` proceeds silently; `reject` skips the capability.

When `tooling.preference` is set to anything other than `auto`, the conductor still detects all available tools, but it ranks the preferred category first unless that category cannot fulfill the capability. The final tool choice and any override are recorded in state.

When `tooling.degraded_mode` is `ask` (the default), the conductor stops and asks the user whether to use a better tool, accept the degraded source, or skip the capability. The disclosure template is in `references/TOOL_SELECTION.md`.

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

  # Tooling preference controls how capabilities are mapped to tools.
  tooling:
    preference: auto              # auto | adapters | mcp | manual
    degraded_mode: ask            # ask | accept | reject

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
