---
name: jira-adapter
description: Issue-tracker source adapter for the pr-report conductor. Resolves Jira tickets and fetches ticket scope with acceptance criteria, returning the normalized issue-tracker shape.
invocation: model-invoked
metadata:
  tags: [pr-report, adapter, issue-tracker-source, jira, building-block]
  author: Wian van der Merwe
  version: "1.0.1"
---

# jira-adapter

Tool building block that implements the `issue-tracker-source` adapter interface for the redesigned `pr-report` skill. It translates Jira issue data into the normalized issue-tracker shape expected by the conductor.

## In scope

- Resolve a Jira ticket key from explicit input, PR title, or PR body.
- Fetch ticket metadata including title, description, status, and acceptance criteria.
- Map Jira statuses and custom fields to the normalized `issue-tracker-source` shape.
- Return the adapter envelope status (`complete`, `partial`, `needs_input`, `blocked`, `skipped`) and confidence.
- Accept configuration provided by `pr-report` (`base_url`, `token`, `project_key`, `custom_fields`, etc.).

## Out of scope

- Synthesizing or triaging scope gaps. The conductor owns that.
- Writing the PR report. The conductor owns that.
- Updating ticket status, comments, or other Jira mutations.
- Handling other issue trackers such as Linear, GitHub Issues, or Azure Boards (use the corresponding adapter).
- Resolving tokens directly. The shared `token-resolver` building block resolves `JIRA_TOKEN` or `JIRA_API_TOKEN`.

## When to use

Use this adapter when the `pr-report` configuration selects it as the issue-tracker source:

```yaml
adapters:
  issue_tracker:
    source: jira-adapter
    config:
      base_url: https://my-org.atlassian.net
      project_key: OC
      token: ${JIRA_TOKEN}
```

## Interface operations

Implements the `issue-tracker-source` interface from `pr-adapter-contract`:

- `resolve_ticket(key, repo, pr_title, pr_body)` → normalized `{ ticket_id, key, url }`
- `fetch_scope(ticket_id)` → normalized `{ key, title, body, acceptance_criteria, status, url }`

## Example input

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

## Example output (worker return contract)

```yaml
---
status: complete
artifacts: []
---

## Summary
Resolved Jira ticket OC-1234 and fetched its scope for owner/repo PR "OC-1234 Fix login flow".

## Findings
adapter_role: issue-tracker-source
ticket:
  ticket_id: "12345"
  key: OC-1234
  title: "Fix login flow"
  body: "As a user, I want to log in securely so that I can access my account."
  acceptance_criteria:
    - "Valid credentials redirect to dashboard."
    - "Invalid credentials show a clear error."
  status: in_progress
  url: https://my-org.atlassian.net/browse/OC-1234

## Decisions made
- Source selected because pr-report config set `issue_tracker.source: jira-adapter`.
- Token resolved via the token-resolver building block from `JIRA_TOKEN`.
- Ticket key extracted from PR title prefix `OC-1234`.
- Acceptance criteria mapped from the configured `customfield_10101` field.

## Open questions
- None.

## Blockers
- None.
```

## Rules

- Return the normalized `issue-tracker-source` shape, not raw Jira API responses.
- Never log or expose the resolved token.
- Distinguish `complete`, `partial`, `needs_input`, `blocked`, and `skipped` clearly.
- If the token is missing or invalid, return `needs_input` with the required env-var name.
- If the ticket is not found or the project is inaccessible, return `blocked` with the error detail.
- If acceptance criteria cannot be extracted from configured fields, return `partial` and explain what is missing.
- If the ticket key is not provided and cannot be inferred from the PR title or body, return `needs_input` with the requested key.
- Reference the adapter contract at `pr-adapter-contract` for envelope shape and status semantics.

## References

- `pr-adapter-contract` skill — adapter interface contract
- `pr-report/references/ADAPTER_ARCHITECTURE.md` — high-level adapter architecture
- `worker-contract` skill — return contract format
- `token-resolver` building block — token resolution
