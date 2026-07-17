# Dependencies

## Required skills

- `pr-adapter-contract` — adapter interface contract.
- `worker-contract` — return contract format.
- `token-resolver` — token resolution.

## Required environment

- Network access to the GitHub API.
- An HTTP-capable tool for GitHub Actions API calls, chosen by the conductor (no bundled script).

## Environment variables

The token is resolved by `token-resolver`. Commonly referenced:

- `GITHUB_TOKEN`
- `GITHUB_PERSONAL_ACCESS_TOKEN`
