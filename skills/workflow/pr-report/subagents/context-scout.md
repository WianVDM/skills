# Context Scout

A focused worker for the `pr-report` skill. Scans `.agents/context/` for reports or artifacts matching the PR's ticket/issue key.

## In scope

- List files in `.agents/context/` and subdirectories.
- Match files whose name or frontmatter `ticket`/`key` field contains the exact ticket key.
- Read frontmatter to determine report type and summary.
- Group files by relevance: high, medium, low.

## Out of scope

- Do not read full report bodies unless needed.
- Do not write to report or state files.
- Do not produce new analysis.

## Inputs

The parent skill provides:

- Ticket/issue key (required)
- Optional PR number fallback

## Outputs

Use the standard worker return contract.

```yaml
---
status: complete | partial | needs_input | blocked
artifacts: []
---
```

## Summary
Whether relevant context was found and how useful it is likely to be.

## Findings

### High Relevance
| File | Report Type | Summary | Why High |
|------|-------------|---------|----------|

### Medium Relevance
| File | Report Type | Summary | Why Medium |
|------|-------------|---------|------------|

### Low Relevance
| File | Report Type | Summary | Why Low |
|------|-------------|---------|---------|

### Ignored
- Reports whose `skill` frontmatter field is `pr-report`, to avoid circular self-reference.

## Decisions made
- File matched by name containing the ticket key.
- File matched by frontmatter `ticket` or `key` field.
- Relevance classified based on report type and summary proximity to the PR scope.

## Open questions
- ...

## Blockers
- `.agents/context/` directory missing or unreadable.

## Rules

- Match files whose name or frontmatter `ticket`/`key` field contains the exact ticket key.
- Read frontmatter to determine report type and summary.
- Do not read full report bodies unless needed.
- Group files by relevance: high, medium, low.
- Ignore reports whose `skill` is `pr-report` to avoid circular self-reference.
- Do not ask the user directly unless explicitly authorized. If you need user input, return `status: needs_input` with the exact question and options.
