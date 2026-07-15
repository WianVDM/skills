# jira-adapter

Issue-tracker source adapter for the `pr-adapter-contract`.

## What it does

Resolves Jira tickets and fetches ticket scope with acceptance criteria in the normalized `issue-tracker-source` shape.

## Files

- `SKILL.md` — adapter definition and contract.
- `references/INTERFACE.md` — input and output schemas.
- `references/DEPENDENCIES.md` — dependencies.
- `evals/evals.json` — trigger evals.

## Dependencies

- `pr-adapter-contract`
- `worker-contract`
- `token-resolver`
