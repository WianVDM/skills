# GitHub PR Adapter Dependencies

## Required skills

- `worker-contract` — canonical worker return format.
- `token-resolver` — resolves the GitHub token without exposing it.

## Required tools

- Network access to GitHub API.
- `read`, `write` for temporary cache or output.

## Required binaries

- Python 3.x or equivalent for API calls.

## Environment

- `GITHUB_TOKEN` or `GITHUB_PERSONAL_ACCESS_TOKEN` referenced via `token-resolver`.
