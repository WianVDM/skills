# manual-pr-adapter

Manual PR source adapter for the `pr-adapter-contract`.

## What it does

Collects PR metadata, changed files, and review feedback from user input, CSV, JSON, or Markdown files and returns them in the normalized `pr-source` shape.

## Files

- `SKILL.md` — adapter definition and contract.
- `references/INTERFACE.md` — input and output schemas.
- `references/DEPENDENCIES.md` — dependencies.
- `evals/evals.json` — trigger evals.

## Dependencies

- `pr-adapter-contract`
- `worker-contract`
