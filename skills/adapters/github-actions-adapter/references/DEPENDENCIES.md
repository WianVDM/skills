# Dependencies

## Required building blocks

- `worker-contract` — canonical return format for adapter output.
- `token-resolver` — resolves the GitHub token from config, env vars, or user input.

## Runtime requirements

- Network access to `api.github.com` and the repository's Actions run URLs.
- Python 3.x (or equivalent HTTP client) for making GitHub API requests.
- `GITHUB_TOKEN` environment variable (or equivalent resolved token) with `repo` scope for private repositories.

## Optional

- Branch protection read access to determine required checks automatically if `required_checks` is not provided.
