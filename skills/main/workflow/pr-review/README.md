# pr-review

A conductor skill that assists the user during a pull-request review.

## What it does

`pr-review` gathers PR context, checks out the branch in a temporary worktree, runs targeted checks on changed files, drafts a review that avoids duplicating existing comments, and posts it only after explicit user approval.

## Workflow

1. **Initialize** — load config, detect required tools.
2. **Resolve PR** — identify the PR from user input.
3. **Discover tools** — rank available tools for each capability.
4. **Collect context** — fetch PR data, reviews, CI status, ticket scope.
5. **Checkout and inspect** — create a worktree, read files, run scoped checks.
6. **Synthesize review** — draft comments using scope, conventions, and existing reviews.
7. **Draft review** — write the review draft to a context report.
8. **Review with user** — present the draft and iterate until confirmed.
9. **Post or hand back** — post via the best tool or provide an exact manual payload.

## Files

- `SKILL.md` — skill definition and workflow.
- `README.md` — this file.
- `config.yaml` — configuration schema.
- `references/` — detailed workflow, tool selection, posting gate, and config rules.
- `subagents/` — workers for normalization, checkout, synthesis, drafting, and posting.
- `evals/evals.json` — trigger and behavior evals.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).
