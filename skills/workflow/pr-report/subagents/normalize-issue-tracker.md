# Normalize Issue Tracker

Follow the `worker-contract` return contract. Normalizes raw issue-tracker tool output into the internal `pr-report` normalization model.

## In scope

- Accept raw ticket scope, acceptance criteria, and status from a tool.
- Map the raw output to the normalized internal model.
- Set confidence based on mapping completeness and quality.
- Handle missing or partial fields gracefully.

## Inputs

- Capability name: `issue_tracker`
- Raw tool output (e.g., from Jira MCP, Jira API, manual input)
- Tool name and provider name (e.g., `jira_mcp`, `jira_api`, `manual`)
- Optional mapping hints for non-standard providers

## Outputs

Return the standard worker contract with a `Findings` section containing the normalized envelope and findings:

### Envelope

```yaml
capability: issue_tracker
status: complete | partial | missing | degraded
tool: string
source: string
confidence: high | medium | low
findings: []
errors: []
better_tool: string | null
```

### Normalized findings

- **Ticket scope:** `key`, `title`, `description`, `acceptance_criteria`, `status`, `linked_prs`.

## Rules

- Map fields that exist; leave missing fields absent rather than inventing defaults.
- Set confidence to `high` only when all required fields are present and the mapping is direct.
- Set confidence to `medium` when acceptance criteria are inferred from description or comments.
- Set confidence to `low` when the ticket status or key is missing or ambiguous.
- Record any degradation notes in `errors` (e.g., missing acceptance criteria, stale ticket).
- Do not write to the report or state files.
- Escalate to `needs_input` if the raw output cannot be mapped at all.
