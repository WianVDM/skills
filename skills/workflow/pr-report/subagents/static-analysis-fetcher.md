# Static Analysis Fetcher

A focused worker for the `pr-report` skill. Fetches static-analysis findings for the PR.

## In scope

- Retrieve findings from the configured static-analysis provider.
- Report open findings with rule, severity, location, and status.
- Confirm the call succeeded even when zero findings are returned.

## Out of scope

- Do not fix findings.
- Do not write to report or state files.

## Inputs

The parent skill provides:

- PR identifier
- Configured static-analysis provider
- Project key / organization
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
Whether findings were retrieved and the overall risk level.

## Findings

### Findings
| Key | Rule | Severity | Message | File | Line | Status | URL |
|-----|------|----------|---------|------|------|--------|-----|

### Provider Notes
- Provider: sonarcloud
- Project key: ...
- Total open findings: N

## Decisions made
- Preferred direct API over MCP fallback because a token was available.
- Verified the correct project was analyzed when zero findings were returned.

## Open questions
- ...

## Blockers
- Provider API or MCP server failed.

## Rules

- Prefer direct API when token is available; fall back to MCP server.
- If zero findings are returned, confirm the call succeeded and the right project was analyzed.
- Do not write to report or state files.
- If the provider fails, return `status: blocked` with the error details.
- Do not ask the user directly unless explicitly authorized. If you need user input, return `status: needs_input` with the exact question and options.
