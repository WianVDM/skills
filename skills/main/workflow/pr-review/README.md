# pr-review

A conductor skill that assists the user during a pull-request review.

## What it does

`pr-review` gathers PR context — including the conversation the PR has already had — checks out the branch in a temporary worktree, runs targeted checks on changed files, and produces two artifacts: a user-facing report with everything it found, and a PR-facing review draft that is ready to post. It posts only after explicit user approval, or hands back an exact manual payload.

## Workflow

0. **Intake** — first run per project: resolve the review style profile.
1. **Initialize** — load config; resolve PR-source and checkout tools (model-first).
2. **Resolve PR** — identify the PR from user input.
3. **Resolve tools** — cached per-project recipes, re-validated or re-derived.
4. **Collect context** — metadata, reviews, threads, conversation comments, diff, CI, ticket scope.
5. **Checkout and inspect** — worktree, full-file reads, scoped checks.
6. **Synthesize** — findings per the review rubric; settled items classified, never re-flagged without consent.
7. **Draft** — user-facing report + PR-facing draft, two separate artifacts.
8. **Review with user** — present both, resolve open questions, iterate to confirmation.
9. **Post or hand back** — one-shot post after coordinate validation, or exact manual payload.

## Files

- `SKILL.md` — skill definition and workflow.
- `README.md` — this file.
- `config.yaml` — configuration schema (tools, style profile, gates).
- `references/` — rubric, report/draft contracts, workflow, posting gate, config, checkpointing, chainlog, validation.
- `subagents/` — check-selector, checkout-coordinator, review-synthesizer, review-writer, posting-coordinator.
- `scripts/` — validate-review-coordinates.py (deterministic diff-hunk coordinate checks).
- `evals/evals.json` — trigger and behavior evals.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).
