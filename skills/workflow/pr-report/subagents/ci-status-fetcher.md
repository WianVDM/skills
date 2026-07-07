# CI Status Fetcher

A focused worker for the `pr-report` skill. Determines whether CI / build checks are passing or failing and summarizes failures.

## In scope

- Query the configured CI provider for the PR head commit.
- Distinguish required and optional checks.
- Fetch and summarize failing job logs when enabled.
- Report overall status and per-check details.

## Out of scope

- Do not fix failing checks.
- Do not write to report or state files.

## Inputs

The parent skill provides:

- PR identifier
- Head commit SHA
- Configured CI provider
- Whether to fetch logs (`ci.fetch_logs`)
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
Overall CI status and whether any action is required.

## Findings

### Overall Status
passing | failing | mixed | unknown

### Check Runs
| Name | Status | Conclusion | Required | URL | Log Summary |
|------|--------|------------|----------|-----|-------------|

### Failures
| Name | Reason | Full Log URL |
|------|--------|--------------|

## Decisions made
- ...

## Open questions
- ...

## Blockers
- CI provider unavailable or token missing.

## Rules

- Distinguish required checks from optional checks.
- If fetching logs, extract error messages and stack traces, then truncate to a readable summary.
- Provide a link to the full log; do not paste the entire log.
- If CI is unavailable, return `status: blocked` with a clear reason.
- Do not ask the user directly unless explicitly authorized. If you need user input, return `status: needs_input` with the exact question and options.
