# Configuration and Notes

`pr-report` uses the config + notes pattern. It detects the environment, asks for missing information once, persists the answers, and reuses them on future runs.

## Canonical location

Config and notes live in the detected project configuration directory:

```text
{config_dir}/pr-report.yaml
```

`{config_dir}` is discovered by the `detect-project-context` building block. The default is `{project-root}/.agents/config`, but the skill does not assume that path. See the `## Initialize` section in `SKILL.md` for the detection routine.

Reports and state live in the detected project context directory:

```text
{context_dir}/pr-report/
```

`{context_dir}` is also discovered by `detect-project-context`. The default is `{project-root}/.agents/context`.

## First-run flow

The initialization phase follows the lazy-loading pattern from the skill standards:

1. Detect the environment, project type, git remote, and available tools.
2. Propose sensible defaults for every value that can be inferred.
3. Ask the user only for values that are ambiguous or impossible to detect.
4. Validate required capabilities eagerly; validate recommended/optional capabilities only when the branch that needs them is selected.
5. Offer a single "Use detected defaults" confirmation step instead of interrogating the user for every config key.
6. Persist resolved config and continue.

The conductor detects the repo from `git remote`, the issue tracker from the remote domain or existing config, and the preferred PR provider from the same signals. It only asks when there are multiple plausible remotes or when no remote exists.

## Tool and provider detection

Provider detection is the default behavior. When a tool provider is set to `auto`, the skill selects the best tool for the capability by inspecting, in order:

- Explicit per-capability tool preferences (`pr-report.tools.{capability}.provider`).
- The global `pr-report.tooling.preference` value.
- Available MCP servers and tools.
- Native binaries (`gh`, `git`, `curl`, etc.).
- Direct APIs and environment variables (only if explicitly configured and confirmed).
- The git remote and project files such as CI configuration.

The skill does not assume a specific harness, model, or tool. It uses the capability-to-tool mapping in `references/TOOL_SELECTION.md`.

### Tooling preference and degraded mode

Two config keys control tool selection behavior globally:

- `pr-report.tooling.preference` — `auto` selects the best available tool; `mcp` prefers MCP tools; `cli` prefers native binaries; `manual` always asks.
- `pr-report.tooling.degraded_mode` — `ask` prompts the user before accepting a degraded source; `accept` proceeds silently; `reject` skips the capability.

When `pr-report.tooling.preference` is set to anything other than `auto`, the conductor still detects all available tools, but it ranks the preferred category first unless that category cannot fulfill the capability. The final tool choice and any override are recorded in state.

When `pr-report.tooling.degraded_mode` is `ask` (the default), the conductor stops and asks the user whether to use a better tool, accept the degraded source, or skip the capability. The disclosure template is in `references/TOOL_SELECTION.md`.

### Token resolution

Tools receive tokens through the shared `token-resolver` building block. Tokens are resolved in this order:

1. Literal value in `pr-report.tools.{capability}.config.token`.
2. `${ENV_VAR}` reference in `pr-report.tools.{capability}.config.token`.
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
pr-report:
  tools:
    pr:
      provider: auto          # auto | github | manual | direct
      repo: null            # default owner/repo; null means detect from git remote
      endpoint: null        # direct API endpoint; only used with provider: direct
    ci:
      provider: auto          # auto | github-actions | none | direct
      endpoint: null
    static_analysis:
      provider: auto          # auto | sonarcloud | none | direct
      endpoint: null
    issue_tracker:
      provider: auto          # auto | jira | none | direct
      endpoint: null
  tooling:
    preference: auto          # auto | mcp | cli | manual
    degraded_mode: ask        # ask | accept | reject
  scope_mode: lenient         # strict | lenient
  task_list:
    enabled: true
  test_mode: false
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

## Self-updates

The skill may append to `notes` and update non-secret fields in place:

- Detected project context directory and source.
- Provider URLs and organizations discovered from MCP config.
- Tool availability/unavailability observations.
- User preference explanations.

Rules:

- **Append-only for notes.** Never delete observations.
- **Do not overwrite user values silently.** If auto-discovery conflicts with an explicit config value, report the conflict and ask.
- **Do not log tokens.** Tokens are referenced by env var names or stored securely; never written into report or state files.
- **Timestamp observations.** Each note should include an ISO date.

## User consultation

When a tool cannot be resolved or its token is missing, explain what was already tried and present options:

1. Paste a token.
2. Provide an environment variable name.
3. Say `skip` to skip this capability this run.
4. Say `disable` to turn off this capability permanently.
