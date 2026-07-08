# jira-adapter

Issue-tracker source adapter for `pr-report`.

## Purpose

Resolve Jira tickets and fetch ticket scope with acceptance criteria, returning the normalized `issue-tracker-source` shape.

## When to use

When `pr-report` config points `adapters.issue_tracker.source` to `jira-adapter` and the project uses Jira Cloud or Jira Server.

## Inputs

| Field | Description |
|---|---|
| `base_url` | Jira instance URL (e.g., `https://my-org.atlassian.net`). |
| `project_key` | Jira project key used for key inference. |
| `token` | Resolved Jira API token (via `token-resolver`). |
| `key` | Explicit Jira ticket key, or inferred from PR title/body. |
| `custom_fields` | Optional mapping of normalized fields to Jira custom field IDs. |

## Outputs

Normalized `issue-tracker-source` data:

- `ticket_id`: numeric Jira issue ID.
- `key`: ticket key (e.g., `OC-1234`).
- `title`, `body`, `status`.
- `acceptance_criteria`: array of acceptance criteria strings.
- `url`: link to the ticket.

See `SKILL.md` for the full interface and worker-return-contract example.
