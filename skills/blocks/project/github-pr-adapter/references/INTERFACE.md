# Interface

`github-pr-adapter` implements the `pr-source` interface from `pr-adapter-contract`.

## Input

```yaml
---
repo: owner/repo
config:
  token: ${GITHUB_TOKEN}
  api_url: https://api.github.com
  graphql_url: https://api.github.com/graphql
---
```

| Field | Required | Description |
|---|---|---|
| `repo` | yes | Repository in `owner/repo` format. |
| `config.token` | yes | GitHub token, resolved by `token-resolver`. |
| `config.api_url` | no | REST API base URL. Default: `https://api.github.com`. |
| `config.graphql_url` | no | GraphQL API URL. Default: `https://api.github.com/graphql`. |

## Operations

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

### `fetch_issue_comments(pr_id)`

Fetches conversation (issue-level) PR comments via `GET /repos/{owner}/{repo}/issues/{pr}/comments`. This is a different surface from review comments: SonarCloud decorations, Codecov, and deploy bots post here.

Output: array of comment objects with:

- `id`, `author`, `body`, `created_at`, `source_type`, `url`

`source_type` is `bot` when the author is a GitHub App or ends in `[bot]`, otherwise `human`.

## Output envelope

The adapter returns the standard `pr-adapter-contract` envelope with `Findings` containing the `pr-source` data.

## Status values

| Status | Meaning |
|---|---|
| `complete` | All requested data fetched and normalized. |
| `partial` | Some data unavailable. |
| `needs_input` | Token missing or invalid, or PR cannot be resolved. |
| `blocked` | API unreachable or repository inaccessible. |
| `skipped` | Not applicable. |

## Rules

- Do not log the token.
- Return `needs_input` if the token is missing or invalid.
- Return `blocked` if the API is unreachable or the repository is inaccessible.
- Normalize timestamps to ISO 8601 UTC.
