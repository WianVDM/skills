# Baseline Configuration and Notes

The `baseline` skill adapts to each project through config and notes stored in `.agents/config/baseline.yaml`.

---

## Config location

```text
{project-root}/.agents/config/baseline.yaml
```

The skill also reads shared project settings from:

```text
{project-root}/.agents/config/shared.yaml
```

User-level skills do not store project context at user level. All generated reports and state live in the project.

---

## Config schema

```yaml
preferences:
  verification_method: auto              # auto | ui | api | test | code-snapshot | manual | none
                                          # or a specific tool from CAPABILITIES.md

  scope:
    default: ask                           # default scope when none is provided: ask | feature | module | route | bug
    feature: null                          # default feature name or route prefix

  branch:
    use_current: true                      # true | false | ask
    target: null                           # explicit branch name when use_current is false

  dev_server:
    url: null                              # detected or ask; no hardcoded default
    auto_start: ask                        # true | false | ask
    start_command: null                    # detected or ask

  viewport: 1280x720

  auth:
    method: none                           # none | existing-session | session-file | env-vars | manual
    session_file: .agents/context/baseline/sessions/default.json
    username_env: AUTH_USERNAME            # only for env-vars
    password_env: AUTH_PASSWORD            # only for env-vars

  output:
    default_format: md                     # md | html-both
    naming: scope-branch                   # scope | scope-branch | ticket

notes:
  - text: "Default verification method is auto-detection; no single tool is assumed."
    category: decision
  - text: "Dev server URL and start command must be detected or resolved per project."
    category: gotcha
```

## Field reference

### `preferences.verification_method`

The primary way the skill captures state. Allowed values:

| Value | Meaning |
|-------|---------|
| `auto` | Detect the best method based on project type and available tools. |
| `ui` | Prefer any UI/browser automation method. |
| `api` | Prefer HTTP/API capture. |
| `test` | Prefer an existing project test runner. |
| `code-snapshot` | Prefer a static code snapshot. |
| `manual` | User provides evidence or description. |
| `none` | Skip capture; produce a minimal report. |
| Specific tool | One of the concrete tools listed in [CAPABILITIES.md](CAPABILITIES.md), e.g. `playwright-mcp`. |

### `preferences.scope`

| Field | Description |
|-------|-------------|
| `default` | Default scope category when the user does not supply one. |
| `feature` | Optional default feature, module, or route prefix. |

### `preferences.branch`

| Field | Description |
|-------|-------------|
| `use_current` | Whether to use the current git branch. `ask` prompts the user. |
| `target` | Explicit branch name when `use_current` is `false`. |

### `preferences.dev_server`

| Field | Description |
|-------|-------------|
| `url` | The URL to navigate to for UI/API baselines. Detected or resolved via user input. |
| `auto_start` | Whether to start the dev server if not running. `ask` prompts the user. |
| `start_command` | The command used to start the dev server. Detected or resolved via user input. |

### `preferences.auth`

| Field | Description |
|-------|-------------|
| `method` | How to handle authenticated pages. |
| `session_file` | Path to saved session cookies/localStorage. |
| `username_env` | Env var name for username. |
| `password_env` | Env var name for password. |

See [AUTH.md](AUTH.md) for details. Auth is optional; only configure it when the target requires authentication.

### `preferences.output`

| Field | Description |
|-------|-------------|
| `default_format` | `md` for Markdown only, `html-both` for Markdown plus HTML gallery. |
| `naming` | Report filename convention: `scope`, `scope-branch`, or `ticket`. |

---

## Bootstrap routine

```text
1. LOAD
   - Read .agents/config/shared.yaml
   - Read .agents/config/baseline.yaml
   - Merge shared values first, then skill-specific

2. DETECT
   - Identify the project type and available capture methods.
   - Detect dev server URL and start command from project files when relevant.
   - Check if the target page or endpoint requires authentication.

3. RESOLVE SCOPE
   - Use the user-provided scope if available.
   - If none, scan .agents/context/ for reports that imply a scope.
   - If still ambiguous, ask the user.

4. RESOLVE BRANCH AND COMMIT
   - Confirm the target branch. If none is specified, use the current branch.
   - Record the current commit hash.
   - If the target branch differs from the current branch, ask the user before switching.

5. VALIDATE
   - Is verification_method set and available, or can it be auto-detected?
   - Is the target (URL, endpoint, or files) reachable or resolvable?
   - Is auth configured for authenticated targets?

6. RESOLVE (only if needed)
   - If verification_method is missing or unavailable, ask the user.
   - If dev_server.url is ambiguous, ask the user.
   - If auth is required but unset, ask the user.
   - Pre-populate options with detected values and previous preferences.
   - Persist the final choices.

7. EXECUTE
   - Capture the baseline using the resolved configuration.

8. CURATE NOTES
   - Add workarounds, preferences, gotchas, or decisions discovered during the run.
   - Remove or update stale notes.
   - Ask the user if a new note contradicts an existing one.
```

---

## User consultation rules

- Never silently overwrite existing config values.
- If detected environment differs from stored config, present the difference and ask.
- Pre-populate questions with detected values and previous preferences.
- Always offer an "Other" or "Ask me later" option.
- Do not silently switch branches. If the target branch differs from the current branch, ask before proceeding.

---

## Note categories

Notes should be concise and future-facing. Use categories from the `write-a-skill` framework:

| Category | Example |
|----------|---------|
| `workaround` | "Playwright MCP cannot access authenticated pages; use a saved session file instead." |
| `preference` | "User prefers HTML galleries for bug baselines." |
| `gotcha` | "Dev server takes ~10 seconds to start; wait before navigating." |
| `decision` | "Default verification method set to auto-detect." |
| `assumption` | "Assuming `/login` is the entry point for auth flows." |

---

## First-run defaults

On first run, the skill has no pre-configured project defaults. It should:

1. Detect the project type and available capture methods.
2. Ask the user to confirm or override the detected `verification_method`.
3. Ask the user to confirm or provide the `dev_server.url` and `start_command` only when a UI or API method is selected.
4. Ask the user to confirm or provide the `scope` and `branch`.
5. Default `output.default_format` to `md` unless the user prefers `html-both`.

Persist the resolved choices in `.agents/config/baseline.yaml`.
