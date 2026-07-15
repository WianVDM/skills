# github-actions-adapter

CI source adapter for the `pr-adapter-contract`.

## What it does

Fetches GitHub Actions check runs and job-log summaries and returns them in the normalized `ci-source` shape.

## Files

- `SKILL.md` — adapter definition and contract.
- `references/INTERFACE.md` — input and output schemas.
- `references/DEPENDENCIES.md` — dependencies.
- `evals/evals.json` — trigger evals.

## Dependencies

- `pr-adapter-contract`
- `worker-contract`
- `token-resolver`
