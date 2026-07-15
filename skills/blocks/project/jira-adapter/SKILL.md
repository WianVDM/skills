---
name: jira-adapter
description: Issue-tracker source adapter that resolves Jira tickets and fetches ticket scope with acceptance criteria, returning the normalized issue-tracker shape.
version: 1.0.0
invocation: model-invoked
depends:
  - pr-adapter-contract
  - worker-contract
  - token-resolver
---

# jira-adapter

Tool building block that implements the `issue-tracker-source` adapter interface. It translates Jira issue data into the normalized issue-tracker shape.

## Skill type

Tool building block.

## When to use

- The configured issue-tracker source is Jira.
- The project uses Jira for ticket tracking.

## In scope

- Resolve a Jira ticket key from explicit input, PR title, or PR body.
- Fetch ticket metadata including title, description, status, and acceptance criteria.
- Map Jira statuses and custom fields to the normalized `issue-tracker-source` shape.
- Return the adapter envelope status and confidence.

## Out of scope

- Synthesizing or triaging scope gaps.
- Writing the PR report.
- Updating ticket status, comments, or other Jira mutations.
- Handling other issue trackers such as Linear, GitHub Issues, or Azure Boards.
- Resolving tokens directly.

## Inputs

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

## Outputs

Standard worker return contract with the `issue-tracker-source` adapter shape.

## Interface operations

- `resolve_ticket(key, repo, pr_title, pr_body)` → normalized `{ ticket_id, key, url }`.
- `fetch_scope(ticket_id)` → normalized `{ key, title, body, acceptance_criteria, status, url }`.

## Completion criteria

- `complete`: Ticket resolved and scope fetched with acceptance criteria.
- `partial`: Scope partially fetched; missing fields listed.
- `needs_input`: Token missing or invalid, or ticket key cannot be inferred.
- `blocked`: Ticket not found or project inaccessible.
- `skipped`: Not applicable.

## Rules

- Return the normalized `issue-tracker-source` shape, not raw Jira API responses.
- Never log or expose the resolved token.
- If acceptance criteria cannot be extracted from configured fields, return `partial`.
- If the ticket key is not provided and cannot be inferred, return `needs_input`.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Dependencies](references/DEPENDENCIES.md)
- [Interface](references/INTERFACE.md)
- `pr-adapter-contract` — adapter interface contract
- `worker-contract` — return contract format
- `token-resolver` — token resolution
