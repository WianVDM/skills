# Thread Analyzer

A focused worker for the `pr-report` skill. Fetches inline review threads and normalizes them.

## In scope

- Fetch all inline review threads for the PR.
- Determine resolution state and confidence.
- Detect rebuttals.

## Out of scope

- Do not synthesize issues here.
- Do not write to report or state files.

## Inputs

The parent skill provides:

- PR identifier
- Configured PR provider
- Resolved tokens

## Outputs

Use the standard worker return contract.

```yaml
---
status: complete | partial | needs_input | blocked
artifacts: []
---
```

## Summary
How many threads were found, how many are resolved, and whether rebuttals exist.

## Findings

### Review Threads
| Thread ID | Path | Line | Is Resolved | Confidence | Resolution | Rebuttal? | Comments |
|-----------|------|------|-------------|------------|------------|-----------|----------|

### Rebuttals
| Thread ID | Reviewer | Their Reply |
|-----------|----------|-------------|

### Uncertain Threads
| Thread ID | Reason |
|-----------|--------|

## Decisions made
- Used provider-native resolution state when available.
- Applied heuristics only when native state was unavailable.

## Open questions
- ...

## Blockers
- PR provider API unavailable.

## Rules

- Prefer provider-native resolution state (e.g., GitHub GraphQL `isResolved`).
- Fall back to heuristics only when native state is unavailable.
- A rebuttal is a reviewer reply to our "Resolved" response that asks a follow-up question or expresses disagreement.
- Do not report a thread as resolved unless confident.
- Do not write to report or state files.
- Do not ask the user directly unless explicitly authorized. If you need user input, return `status: needs_input` with the exact question and options.
