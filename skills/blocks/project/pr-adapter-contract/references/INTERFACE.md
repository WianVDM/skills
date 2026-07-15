# Interface

`pr-adapter-contract` defines the normalized interface between conductors and adapters.

## Adapter envelope

Every adapter returns a result envelope with the following frontmatter:

| Field | Required | Description |
|---|---|---|
| `status` | yes | One of `complete`, `partial`, `needs_input`, `blocked`, `skipped`. |
| `source_type` | yes | Provider identifier (e.g., `github`, `gitlab`, `manual`, `teams`). |
| `adapter` | yes | Adapter skill name (e.g., `github-pr-adapter`). |
| `confidence` | yes | `high`, `medium`, or `low`. |

The body of the envelope contains:

- `Summary` — brief statement of what was found or why it failed.
- `Findings` — the normalized data for this source type.
- `Decisions made` — how the adapter resolved choices.
- `Open questions` — questions for the conductor.
- `Blockers` — external blockers, if any.

## Status semantics

| Status | Meaning | Conductor behavior |
|---|---|---|
| `complete` | Data fetched successfully. | Use the data. |
| `partial` | Some data fetched, but not all. | Use what is available and note gaps. |
| `needs_input` | The adapter needs a token, URL, or file from the user. | Ask the user and retry. |
| `blocked` | A configured adapter failed to connect. | Stop and consult the user. |
| `skipped` | The adapter is missing or disabled. | Continue without that source. |

## PR source operations

### `resolve_pr(user_input, repo, current_branch)`

Output:

```json
{
  "pr_number": 42,
  "repo": "owner/repo",
  "branch": "feature/OC-1234",
  "base": "main",
  "ticket_key": "OC-1234",
  "url": "https://github.com/owner/repo/pull/42"
}
```

### `fetch_metadata(pr_id)`

Output fields:

- `title`, `body`, `author`, `state`, `draft`, `base`, `head`, `mergeable`, `review_decision`

### `fetch_changed_files(pr_id)`

Output: array of file objects with:

- `path`, `status`, `additions`, `deletions`, `previous_path`

### `fetch_reviews(pr_id)`

Output: array of review objects with:

- `id`, `reviewer`, `state`, `body`, `submitted_at`

### `fetch_review_threads(pr_id)`

Output: array of thread objects with:

- `path`, `line`, `is_resolved`, `resolution`, `source_type`, `comments`

## CI / build operations

### `fetch_check_runs(pr_id, head_commit_sha)`

Output: object with `status` and `checks` array. Each check has:

- `name`, `status`, `conclusion`, `url`, `is_required`, `summary`

### `fetch_job_log_summary(failing_check)`

Output:

- `summary`, `full_log_url`, `error_lines`

## Static-analysis operations

### `fetch_findings(pr_id, project_key)`

Output: array of findings with:

- `key`, `rule`, `severity`, `message`, `path`, `line`, `status`, `url`, `source_type`

## Issue-tracker operations

### `resolve_ticket(key, repo, pr_title, pr_body)`

Output:

- `ticket_id`, `key`, `url`

### `fetch_scope(ticket_id)`

Output:

- `key`, `title`, `body`, `acceptance_criteria`, `status`, `url`

## Notification operations

### `fetch_feedback(pr_id, ticket_key, config)`

Output: array of comments with:

- `id`, `author`, `body`, `created_at`, `source_type`, `channel`, `severity`, `file`, `line`, `url`

## Context-report operations

### `discover_reports(key, pr_number, repo, branch)`

Output: array of reports with:

- `path`, `skill`, `relevance`, `summary`

## Adapter rules

- Return the normalized shape, not raw provider data.
- Never log or expose the resolved token.
- If the token is missing or invalid, return `needs_input` with the required env-var name.
- If the provider is unreachable, return `blocked` with the error detail.
- If only partial data is available, return `partial` and note what is missing.
- Mark required checks explicitly using `is_required`.
