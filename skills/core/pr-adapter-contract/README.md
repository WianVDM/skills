# PR Adapter Contract

Defines the normalized interface between the `pr-report` conductor and its adapters.

## What this file owns

- Adapter roles (`pr-source`, `ci-source`, `static-analysis-source`, `issue-tracker-source`, `notification-source`, `context-report-source`).
- Result envelope and status semantics.
- Operation and output shapes for each role.
- Adapter rules (normalization, token handling, status values).

## Who uses it

- Adapter authors implementing a new `pr-report` adapter.
- The `pr-report` conductor when invoking adapters.
- Any other conductor that wants to use the same adapter taxonomy.

## When to update

- The adapter envelope or status semantics change.
- A new adapter role is added.
- Operation signatures or required fields change.
- A new rule is needed for all adapters.

## Layout

- `SKILL.md` — the contract.
- `references/DEPENDENCIES.md` — required skills and tools.
- `evals/evals.json` — trigger evals.

## Conventions

- Keep the contract harness-agnostic and provider-agnostic.
- Never put provider-specific implementation details here; those belong in individual adapter skills.
- Coordinate changes with `pr-report` and all adapter skills so the contract remains the single source of truth.
