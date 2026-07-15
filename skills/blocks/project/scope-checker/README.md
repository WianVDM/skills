# scope-checker

A reusable building block that classifies findings against a scope envelope.

## What it does

`scope-checker` takes a list of findings (PR comments, static-analysis issues, CI failures, or manual observations) and a scope description, then classifies each finding as `in-scope`, `out-of-scope`, or `ambiguous`.

## How to use it

A conductor invokes the subagent at `subagents/scope-checker.md` and provides:

- A `scope` envelope (ticket, PR, branch, commit, or manual description).
- A `findings` array.
- Optional `project_conventions` references.

The subagent returns classified findings following the `worker-contract` format.

## Files

- `SKILL.md` — skill definition and public contract.
- `subagents/scope-checker.md` — subagent prompt.
- `references/INTERFACE.md` — input and output schemas.
- `references/DEPENDENCIES.md` — dependencies and required skills.
- `evals/evals.json` — trigger and behavior evals.

## Dependencies

- `worker-contract` for the return format.
