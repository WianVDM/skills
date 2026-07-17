# Dependencies

## Required skills

- `pr-adapter-contract` — adapter interface contract.
- `worker-contract` — return contract format.
- `token-resolver` — token resolution.

## Required environment

- Network access to the Jira API.
- An HTTP-capable tool for Jira API calls, chosen by the conductor (no bundled script).

## Environment variables

Jira Cloud uses Basic auth: an account email paired with an API token. Both are resolved by `token-resolver`. Commonly referenced:

- `JIRA_TOKEN` or `JIRA_API_TOKEN` — the API token.
- `JIRA_EMAIL` or `JIRA_USER` — the account email for Basic auth.

Without the email/token pair, most Jira instances return 401 and the adapter returns `blocked`.
