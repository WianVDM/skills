# Config pattern

`debrief` reads its project-specific configuration from `{marker_dir}/config/debrief.yaml`. The file is created, migrated, and loaded by the `initialize-skill` building block, which merges `{marker_dir}/config/shared.yaml` and `{marker_dir}/config/debrief.yaml` with the skill-level defaults from `debrief/config.yaml`.

For the full initialization interface, see `initialize-skill/references/INTERFACE.md`.

## Full schema

```yaml
# debrief.yaml
green_threshold: 85            # integer; maps to confidence_level Green
yellow_threshold: 60           # integer; maps to confidence_level Yellow, otherwise Red
baseline_mode: "optional"      # enum: optional | skip | required
issue_tracker: "auto"          # enum: auto | jira | github | linear | manual
max_resolution_loops: 2        # integer; max times the user can add info before a Red report is accepted
freshness_hours: 24            # integer; report age considered fresh
explore_code_max_files: 20     # integer; file-count limit for explore-code
max_history_rows: 20           # integer; checkpoint history row limit before archive

# Confidence penalty config
penalty_challenged: 10         # integer; subtracted per challenged assumption
penalty_unresolved: 10         # integer; subtracted per unresolved assumption
penalty_contradiction: 15      # integer; subtracted per contradiction
penalty_ambiguity: 5           # integer; subtracted per unresolved ambiguity
penalty_inconclusive: 5        # integer; subtracted per inconclusive assumption

# Tracker-specific config
trackers:
  jira:
    server_url: "https://your-domain.atlassian.net"
    token_env: "JIRA_API_TOKEN"
    username_env: "JIRA_USERNAME"
  github:
    token_env: "GITHUB_TOKEN"
    repo_env: "GITHUB_REPO"
  linear:
    token_env: "LINEAR_API_TOKEN"
    team_env: "LINEAR_TEAM"
```

## Defaults

```yaml
green_threshold: 85
yellow_threshold: 60
baseline_mode: "optional"
issue_tracker: "auto"
max_resolution_loops: 2
freshness_hours: 24
explore_code_max_files: 20
max_history_rows: 20
penalty_challenged: 10
penalty_unresolved: 10
penalty_contradiction: 15
penalty_ambiguity: 5
penalty_inconclusive: 5
```

## Slug generation

The report filename uses `{key}-{slug}.md`. The slug is derived from the ticket title by:

1. Lowercasing the title.
2. Replacing non-alphanumeric characters with hyphens.
3. Collapsing consecutive hyphens.
4. Truncating to 50 characters.
5. Appending a 6-character hash of the title if needed to avoid collisions.

Example: `Auth guard race condition` → `OC-4644-auth-guard-race-condition.md`.

## Validation rules

- `green_threshold` and `yellow_threshold` must be integers between 0 and 100.
- `green_threshold` must be greater than `yellow_threshold`.
- `baseline_mode` must be one of `optional`, `skip`, `required`.
- `issue_tracker` must be one of `auto`, `jira`, `github`, `linear`, `manual`.
- If `issue_tracker` is not `auto`, the corresponding `trackers.{name}` block must be present.
- `token_env` values are env var names, not secret values.
- Penalty keys (`penalty_challenged`, `penalty_unresolved`, `penalty_contradiction`, `penalty_ambiguity`, `penalty_inconclusive`) must be non-negative integers.
