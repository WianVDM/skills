# pr-adapter-contract

A normalized adapter interface contract for conductor skills that consume PR metadata, reviews, CI status, static-analysis findings, issue-tracker scope, notifications, and context reports.

## What it does

This building block defines the envelope, status values, operations, and output shapes that adapters must implement. Conductors use the contract to select adapters and consume their data without knowing provider-specific details.

## Adapter roles

- `pr-source`
- `ci-source`
- `static-analysis-source`
- `issue-tracker-source`
- `notification-source`
- `context-report-source`

## Files

- `SKILL.md` — skill definition and contract overview.
- `references/INTERFACE.md` — full operation and output schemas.
- `references/DEPENDENCIES.md` — dependencies and required skills.
- `evals/evals.json` — trigger evals.

## Dependencies

- `worker-contract`
- `context-reports`
- `token-resolver`
