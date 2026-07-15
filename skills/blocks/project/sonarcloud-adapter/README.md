# sonarcloud-adapter

Static-analysis source adapter for the `pr-adapter-contract`.

## What it does

Fetches SonarCloud findings and returns them in the normalized `static-analysis-source` shape.

## Files

- `SKILL.md` — adapter definition and contract.
- `references/INTERFACE.md` — input and output schemas.
- `references/DEPENDENCIES.md` — dependencies.
- `evals/evals.json` — trigger evals.

## Dependencies

- `pr-adapter-contract`
- `worker-contract`
- `token-resolver`
