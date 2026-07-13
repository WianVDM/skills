# Context Scout

Follow the `worker-contract` return contract. Scans `{context_dir}` for reports matching the PR's ticket/issue key and ranks them by relevance.

## In scope

- List files in the detected `{context_dir}` and subdirectories.
- Match files whose name or frontmatter `ticket`/`key` field contains the exact ticket key.
- Read frontmatter to determine report type and summary.
- Group files by relevance: high, medium, low.

## Out of scope

- Reading full report bodies unless needed.
- Writing to report or state files.
- Producing new analysis.

## Inputs

- Ticket/issue key (required)
- Context directory path (required)
- Optional PR number fallback

## Outputs

Return the standard worker contract with a `Findings` section containing:

- High-relevance reports
- Medium-relevance reports
- Low-relevance reports
- Ignored reports (self-referential `pr-report` files)

## Rules

- Match by filename or frontmatter `ticket`/`key`.
- Read only frontmatter unless the summary is unclear.
- Ignore reports whose `skill` is `pr-report` to avoid circular self-reference.
- Escalate to `needs_input` if the context directory is missing or unreadable.
