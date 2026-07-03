# Baseline Configuration and Notes

Config and notes are stored in `.agents/config/baseline.yaml`. Shared settings are read from `.agents/config/shared.yaml` if present. All project context stays in the project.

---

## Config schema

```yaml
preferences:
  verification_method: auto              # auto | ui | api | test | code-snapshot | manual | none

  scope:
    default: ask                           # ask | feature | module | route | bug
    feature: null

  branch:
    use_current: true                      # true | false | ask
    target: null

  runtime:
    url: null
    auto_start: ask                        # true | false | ask
    start_command: null

  viewport: null                           # only for UI methods

  auth:
    method: none                           # none | existing-session | session-file | env-vars | manual
    session_file: null
    username_env: AUTH_USERNAME
    password_env: AUTH_PASSWORD

  output:
    default_format: md                     # md | html-both
    naming: scope-branch                   # scope | scope-branch | ticket

notes:
  - text: "Default verification method is auto-detection."
    category: decision
  - text: "Runtime URL and start command are detected per project."
    category: gotcha
```

## Field reference

| Field | Purpose |
|---|---|
| `verification_method` | How to capture: `auto` or a specific method category/tool. |
| `scope.default` | What to do when no scope is provided. |
| `scope.feature` | Optional default feature, module, or route prefix. |
| `branch.use_current` | Whether to use the current git branch. |
| `branch.target` | Explicit branch when not using current. |
| `runtime.url` | Target URL or endpoint for UI/API baselines. |
| `runtime.auto_start` | Whether to start the runtime if not running. |
| `runtime.start_command` | Command to start the runtime. |
| `viewport` | Viewport size for UI/browser methods only. |
| `auth.method` | Authentication strategy. |
| `auth.session_file` | Saved session file path. |
| `auth.username_env` / `password_env` | Env var names for credentials. |
| `output.default_format` | `md` or `html-both`. |
| `output.naming` | Report filename convention. |

## Bootstrap routine

1. **Load** — read shared config, then skill-specific config.
2. **Detect** — project type, capture methods, runtime URL/command, auth needs.
3. **Resolve scope** — from user input or matching context reports; ask if ambiguous.
4. **Resolve branch and commit** — use current branch unless specified; ask before switching.
5. **Validate** — method is available, target is reachable, auth is configured.
6. **Resolve** — ask the user for missing values, pre-populating with detected values and previous preferences. Persist choices.
7. **Execute** — capture the baseline.
8. **Curate notes** — record workarounds, preferences, gotchas, or decisions; remove stale notes; ask on contradictions.

## User consultation rules

- Never silently overwrite existing config values.
- Show detected vs. stored differences and ask.
- Pre-populate questions with detected values and previous preferences.
- Offer an "Other" or "Ask me later" option.
- Ask before switching branches.

## Note categories

Notes should be concise and future-facing. Use: `workaround`, `preference`, `gotcha`, `decision`, `assumption`.

## First-run defaults

On first run, the skill has no project defaults. It should:

1. Detect project type and capture methods.
2. Ask the user to confirm or override `verification_method`.
3. Ask for `runtime.url` and `start_command` only when the method requires a runtime.
4. Ask for `scope` and `branch`.
5. Ask for `viewport` only for UI/browser methods.
6. Default `output.default_format` to `md` unless the user prefers `html-both`.

Persist the resolved choices in `.agents/config/baseline.yaml`.
