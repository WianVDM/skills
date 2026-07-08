# PR Adapter Contract

Defines the normalized interface between the `pr-report` conductor and its adapters.

## What it covers

- Adapter roles (`pr-source`, `ci-source`, `static-analysis-source`, `issue-tracker-source`, `notification-source`, `context-report-source`).
- Result envelope with status semantics.
- Operation and output shapes for each role.
- Adapter rules (normalization, token handling, status values).

## Who uses it

- Adapter authors implementing a new `pr-report` adapter.
- The `pr-report` conductor when invoking adapters.
- Any other conductor that wants to use the same adapter taxonomy.

## Layout

- `SKILL.md` — the contract.
- `references/DEPENDENCIES.md` — required skills and tools.
- `evals/evals.json` — trigger evals.
