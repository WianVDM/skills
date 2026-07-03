# Debrief Configuration and Notes

The `debrief` skill adapts to each project through config and notes stored in `.agents/config/debrief.yaml`.

---

## Config location

```text
{project-root}/.agents/config/debrief.yaml
```

The skill also reads shared project settings from:

```text
{project-root}/.agents/config/shared.yaml
```

User-level skill settings are not used for project context. All generated reports and state live in the project.

---

## Config schema

```yaml
preferences:
  baseline_mode: required          # required | optional | skip
  issue_tracker: auto                # auto | jira | github | linear | manual
  project_key: null                  # auto-detected from branch or user input
  auto_resolve_ambiguities: true
  max_code_search_minutes: 5       # time-box per ambiguity

  trackers:
    jira:
      server_url: https://your-domain.atlassian.net
      username: your-email@example.com
      token_env: JIRA_API_TOKEN
      username_env: JIRA_USERNAME
      mcp_server_name: jira

    github:
      repo: owner/repo
      token_env: GITHUB_TOKEN

    linear:
      team_key: ENG
      token_env: LINEAR_API_KEY
```

---

## Field reference

### `preferences.baseline_mode`

How strictly the skill should require a baseline:

- `required` — invoke baseline and do not silently skip it.
- `optional` — invoke baseline when it applies; consult the user before skipping a relevant ticket.
- `skip` — do not invoke baseline for this project.

### `preferences.issue_tracker`

The primary issue tracker. Allowed values:

- `auto` — detect from environment and available MCP servers.
- `jira`
- `github`
- `linear`
- `manual`

See [references/trackers/](trackers/) for per-tracker details.

### `preferences.project_key`

The project key used to identify tickets. Resolved in this order:

1. User-provided ticket key.
2. Current branch name (e.g., `PROJ-123-feature-x` → `PROJ`).
3. Existing config.
4. Ask the user.

### `preferences.auto_resolve_ambiguities`

Whether the skill should attempt to resolve ambiguities through codebase exploration before escalating.

### `preferences.trackers.{name}`

Tracker-specific settings. Each tracker adapter defines its own keys. Common fields:

| Field | Description |
|-------|-------------|
| `server_url` | Server URL for the tracker. |
| `username` | Username or email for authentication. |
| `token_env` | Env var name for the API token. |
| `username_env` | Env var name for the username. |
| `mcp_server_name` | Name of the configured MCP server, if applicable. |

---

## Bootstrap routine

```text
1. LOAD
   - Read .agents/config/shared.yaml
   - Read .agents/config/debrief.yaml
   - Merge shared values first, then skill-specific

2. DETECT
   - Run scripts/detect-issue-tracker.py to identify available trackers.
   - Run scripts/extract-ticket-key.py on the current branch to infer the project key.
   - Check codebase access.
   - Inspect current branch for project key as a fallback.

3. VALIDATE
   - Is issue_tracker set and available?
   - Is project_key resolvable?
   - Are tracker credentials accessible?

4. RESOLVE (only if needed)
   - If issue_tracker is auto or missing, ask the user with detected options.
   - If project_key is missing, ask the user or infer from branch.
   - Pre-populate options with detected values and previous preferences.
   - Persist the final choices.

5. EXECUTE
   - Run the debrief workflow using resolved configuration.

6. CURATE NOTES
   - Add workarounds, preferences, gotchas, or decisions.
   - Remove or update stale notes.
   - Ask the user if contradictions arise.
```

---

## User consultation rules

- Never silently overwrite existing config values.
- If detected environment differs from stored config, present the difference and ask.
- Pre-populate questions with detected values and previous preferences.
- Always offer an "Other" or "Ask me later" option.

---

## Note categories

Notes should be concise and future-facing:

| Category | Example |
|----------|---------|
| `workaround` | "Jira MCP does not return changelog; use issue dates API instead." |
| `preference` | "User prefers manual fallback over GitHub token setup." |
| `gotcha` | "Tickets in this project often lack acceptance criteria." |
| `decision` | "Issue tracker set to Jira; project key 'PROJ'." |
| `assumption` | "Assuming `main` is the default branch for context lookup." |

---

## First-run defaults

On first run, the skill has no project-specific defaults. It will:

1. Detect available trackers using `scripts/detect-issue-tracker.py`.
2. Extract a candidate project key from the current branch using `scripts/extract-ticket-key.py`.
3. Present the detected options and ask the user to confirm or override.
4. Persist the user's choices in `.agents/config/debrief.yaml`.

The user can accept or override each detected value. No domain, project key, or email is pre-populated.

---

## Deterministic helpers

- `scripts/detect-issue-tracker.py` — lists available trackers and their confidence.
- `scripts/extract-ticket-key.py` — extracts a ticket key from a branch name or text.
- `scripts/check-debrief-freshness.py` — checks whether an existing debrief report is still current.
- `scripts/scan-related-context.py` — scans `.agents/context/` for reports related to the current ticket or branch.
