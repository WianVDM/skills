# Interface

`jira-adapter` implements the `issue-tracker-source` interface from `pr-adapter-contract`.

## Input

```yaml
config:
  base_url: https://my-org.atlassian.net
  project_key: OC
  token: ${JIRA_TOKEN}
  custom_fields:
    acceptance_criteria: customfield_10101
input:
  key: OC-1234
  repo: owner/repo
  pr_title: "OC-1234 Fix login flow"
  pr_body: "..."
```

| Field | Required | Description |
|---|---|---|
| `config.base_url` | yes | Jira instance URL. |
| `config.project_key` | yes | Jira project key. |
| `config.token` | yes | Jira token, resolved by `token-resolver`. |
| `config.custom_fields.acceptance_criteria` | no | Custom field ID for acceptance criteria. |
| `input.key` | no | Ticket key; inferred from PR title/body if omitted. |
| `input.repo` | no | Repository context. |
| `input.pr_title` | no | PR title for key inference. |
| `input.pr_body` | no | PR body for key inference. |

## Operations

### `resolve_ticket(key, repo, pr_title, pr_body)`

Output:

```json
{
  "ticket_id": "12345",
  "key": "OC-1234",
  "url": "https://my-org.atlassian.net/browse/OC-1234"
}
```

### `fetch_scope(ticket_id)`

Output:

```yaml
key: OC-1234
title: "Fix login flow"
body: "As a user, I want to log in securely so that I can access my account."
acceptance_criteria:
  - "Valid credentials redirect to dashboard."
  - "Invalid credentials show a clear error."
status: in_progress
url: https://my-org.atlassian.net/browse/OC-1234
```

## Output envelope

The adapter returns the standard `pr-adapter-contract` envelope with `Findings` containing the `issue-tracker-source` data.

## Status values

| Status | Meaning |
|---|---|
| `complete` | Ticket resolved and scope fetched. |
| `partial` | Scope partially fetched. |
| `needs_input` | Token missing or invalid, or key cannot be inferred. |
| `blocked` | Ticket not found or project inaccessible. |
| `skipped` | Not applicable. |

## Rules

- Return normalized `issue-tracker-source` shape, not raw Jira API responses.
- Never log or expose the token.
- If acceptance criteria cannot be extracted, return `partial`.
- If key cannot be inferred, return `needs_input`.
