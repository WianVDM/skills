# Debrief Configuration and Notes

The `debrief` skill adapts to each project through config and notes stored in the detected project marker directory.

## Config location

Config lives at:

```text
{marker_dir}/config/debrief.yaml
```

The skill also reads shared project settings from:

```text
{marker_dir}/config/shared.yaml
```

`{marker_dir}` is detected at runtime using `.agents`, `.pi`, `agents`, or a user-specified marker directory. The skill no longer assumes a hardcoded `.agents/` path.

User-level skill settings are not used for project context. All generated reports and state live in the project context directory.

## Config schema

```yaml
preferences:
  confidence_threshold: 85          # 0-100; below this = stop and escalate
  baseline_mode: optional           # required | optional | skip
  issue_tracker: auto               # auto | jira | github | linear | manual
  project_key: null                 # auto-detected or user-provided
  max_parallel_subagents: 3         # 1-N
  max_related_depth: 3              # levels of related-work exploration
  max_investigation_rounds: 5       # rounds per ambiguity before user trigger
  max_code_search_minutes: 5        # per ambiguity
  artifact_freshness_hours: 24      # stale artifact threshold
  auto_resolve_ambiguities: true    # attempt autonomous resolution before escalating
  monorepo_workspace: auto          # auto | package-name | null

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
      mcp_server_name: github

    linear:
      team_key: ENG
      token_env: LINEAR_API_KEY
      mcp_server_name: linear

notes:
  - text: "Example note"
    category: gotcha  # workaround | preference | gotcha | decision | assumption
```

## Field reference

| Field | Description |
|---|---|
| `confidence_threshold` | Minimum confidence (%) for a successful debrief. Default 85. |
| `baseline_mode` | How strictly baseline is required. |
| `issue_tracker` | Primary tracker. `auto` lets the skill detect. |
| `project_key` | Used to validate ticket keys. |
| `max_parallel_subagents` | Concurrency limit for independent subagents. |
| `max_related_depth` | How many levels of related tickets to explore. |
| `max_investigation_rounds` | Per-ambiguity round limit before user trigger. |
| `max_code_search_minutes` | Time-box per ambiguity. |
| `artifact_freshness_hours` | How old an artifact can be before it is flagged stale. |
| `auto_resolve_ambiguities` | Whether to attempt resolution before asking the user. |
| `monorepo_workspace` | Which workspace to scope searches to. |

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
|---|---|
| `server_url` | Server URL for the tracker. |
| `username` | Username or email for authentication. |
| `token_env` | Env var name for the API token. |
| `username_env` | Env var name for the username. |
| `mcp_server_name` | Name of the configured MCP server, if applicable. |

## Config validation

On load, the skill validates:

- `confidence_threshold` is an integer between 0 and 100. If not, clamp to 85.
- `max_parallel_subagents` is a positive integer. If not, default to 3.
- `max_related_depth`, `max_investigation_rounds`, `max_code_search_minutes`, and `artifact_freshness_hours` are positive. If not, use defaults.
- `baseline_mode` is one of `required`, `optional`, `skip`. If not, default to `optional`.
- `issue_tracker` is one of `auto`, `jira`, `github`, `linear`, `manual`. If not, default to `auto`.

Invalid values are reported to the user and replaced with defaults.

## Multiple trackers

The skill supports multiple configured trackers, but one tracker is used as the **primary** source per debrief.

- `issue_tracker` selects the primary tracker. If set to `auto`, the skill picks the first available tracker with the highest confidence.
- If the primary tracker fails or is unavailable, the skill offers the user a choice of the next available tracker or manual fallback.
- The skill does not merge results from multiple trackers unless the user explicitly asks it to.
- All trackers can be configured in `debrief.yaml` simultaneously; only the active one is used per run.

## Config notes lifecycle

Notes are persisted in `debrief.yaml` under the `notes` list. They are future-facing memory, not logs.

- **Add a note** when:
  - The skill makes a decision that should persist (e.g., tracker choice, project key).
  - A workaround or gotcha is discovered.
  - A user preference is expressed.
- **Review notes** at the start of each run. If a note contradicts detected reality, surface it to the user.
- **Update or remove** stale notes only after user confirmation.
- **Categories:** `workaround`, `preference`, `gotcha`, `decision`, `assumption`.

## Bootstrap routine

```text
1. DETECT
   - Run scripts/detect-project-layout.py to identify the project marker directory.
   - Run scripts/detect-issue-tracker.py to identify available trackers.
   - Run scripts/extract-ticket-key.py on the current branch to infer the project key.
   - Check codebase access.

2. LOAD
   - Read {marker_dir}/config/shared.yaml
   - Read {marker_dir}/config/debrief.yaml
   - Merge shared values first, then skill-specific; populate missing v4 keys with defaults.

3. VALIDATE
   - Is issue_tracker set and available?
   - Is project_key resolvable?
   - Are tracker credentials accessible?
   - Are new v4 config keys valid?

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

## User consultation rules

- Never silently overwrite existing config values.
- If detected environment differs from stored config, present the difference and ask.
- Pre-populate questions with detected values and previous preferences.
- Always offer an "Other" or "Ask me later" option.

## Note categories

Notes should be concise and future-facing:

| Category | Example |
|---|---|
| `workaround` | "Jira MCP does not return changelog; use issue dates API instead." |
| `preference` | "User prefers manual fallback over GitHub token setup." |
| `gotcha` | "Tickets in this project often lack acceptance criteria." |
| `decision` | "Issue tracker set to Jira; project key 'PROJ'." |
| `assumption` | "Assuming `main` is the default branch for context lookup." |

## First-run defaults

On first run, the skill has no project-specific defaults. It will:

1. Detect the project marker directory using `scripts/detect-project-layout.py`.
2. Detect available trackers using `scripts/detect-issue-tracker.py`.
3. Extract a candidate project key from the current branch using `scripts/extract-ticket-key.py`.
4. Present the detected options and ask the user to confirm or override.
5. Persist the user's choices in `{marker_dir}/config/debrief.yaml`.

The user can accept or override each detected value. No domain, project key, or email is pre-populated.

## Migration from v3

- Existing v3 config files are merged with v4 defaults.
- Missing v4 keys are populated with defaults and the user is notified.
- Existing state files are upgraded in place on first write.
- v3 reports can be read by v4 consumers, but v4 consumers should regenerate if they need the new fields (`task_type`, `confidence_gap`, `assumptions`).

## Deterministic helpers

- `scripts/detect-project-layout.py` — find the project marker directory.
- `scripts/detect-issue-tracker.py` — lists available trackers and their confidence.
- `scripts/extract-ticket-key.py` — extracts a ticket key from a branch name or text.
- `scripts/infer-ticket-type.py` — classifies the ticket type.
- `scripts/detect-verifiable-state.py` — decides whether baseline is relevant.
- `scripts/check-debrief-freshness.py` — checks whether an existing debrief report is still current.
- `scripts/scan-related-context.py` — scans the context directory for reports related to the current ticket or branch.
- `scripts/find-related-prs.py` — finds PRs related to the ticket or files.
- `scripts/trace-bug-origin.py` — traces a bug to its original feature commit.
