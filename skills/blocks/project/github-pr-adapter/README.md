# github-pr-adapter

GitHub PR source adapter for the `pr-adapter-contract`.

## What it does

Fetches PR metadata, changed files, reviews, and inline review threads from the GitHub API and returns them in the normalized `pr-source` shape.

## Files

- `SKILL.md` — adapter definition and contract.
- `references/INTERFACE.md` — input and output schemas.
- `references/DEPENDENCIES.md` — dependencies.
- `evals/evals.json` — trigger evals.

## Dependencies

- `pr-adapter-contract`
- `worker-contract`
- `token-resolver`
