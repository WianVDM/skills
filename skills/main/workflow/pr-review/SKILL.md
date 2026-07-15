---
name: pr-review
description: Help the user review a pull request by gathering context, checking the branch locally in a worktree, running targeted checks on changed files, drafting a review that does not duplicate existing comments, and posting it only after explicit user approval. If posting confidence is not high, it hands back an exact manual payload.
version: 1.0.0
invocation: model-invoked
depends:
  - detect-project-context
  - initialize-skill
  - context-reports
  - worker-contract
  - token-resolver
  - identity-resolver
  - tool-discovery
  - artifact-freshness
  - evidence-store
  - git-worktree-inspector
  - scope-checker
  - pr-adapter-contract
---

# pr-review

## Purpose

Act as an assistant during a human pull-request review. Gather context, inspect the changed code locally, run targeted checks, draft a review that avoids duplicating existing comments, and post it only after explicit user approval.

## Skill type

Conductor. It coordinates tools and subagents to prepare and optionally post a review.

## When to use

- The user says `/pr-review`, `review this PR`, `review pull request`, or `help me review`.
- The user provides a PR number, ticket key, branch name, or PR URL.
- The user wants local inspection and targeted checks before drafting a review.
- The user wants a review draft that does not repeat existing comments.
- The user wants safe posting with a manual fallback when tools are not trustworthy.

## Core contract

Accept a PR identifier, resolve the PR, discover the best available tools, collect context, check out the branch in a worktree, run scoped checks, synthesize a review draft, confirm it with the user, and either post it or hand back an exact manual payload.

## In scope

- Resolve PR identity from a number, ticket key, branch name, or URL.
- Discover the best available tool for every load-bearing capability.
- Collect PR metadata, existing reviews, inline threads, changed files, CI status, and ticket scope.
- Check out the PR branch via `git-worktree-inspector` without disturbing the user's current branch.
- Read changed files locally and run targeted checks on them.
- Synthesize a review draft that considers ticket scope and project conventions.
- Avoid duplicating existing review comments.
- Distinguish required changes from optional suggestions.
- Anchor inline comments to changed diff hunks.
- Write the review draft to a context report.
- Present the draft, ask for feedback, iterate, and require explicit approval before posting.
- Post via the best available tool after approval, or hand back an exact manual payload.
- Record tool selections, confidence levels, and decisions in state.

## Out of scope

- Implementing fixes or writing replies to PR comments.
- Resolving, dismissing, or editing existing threads.
- Approving or merging without explicit user confirmation.
- Treating any single tool or provider as the only source of truth.
- Posting placeholder reviews, "test" reviews, or partial reviews.
- Running full-project checks that touch files outside the PR scope.

## Workflow

1. **Initialize** — detect project context, load or create `{config_dir}/pr-review.yaml`, discover required capabilities, record state. **Completion:** config exists, every required capability has at least one detected tool.
2. **Resolve PR** — invoke `identity-resolver` to get `pr_number`, `repo`, `branch`, `base`, `ticket_key`, `url`. If `needs_input`, ask the user. Check prior reports with `artifact-freshness`. **Completion:** identity recorded in state.
3. **Discover tools** — for each capability (PR source, reviews, changed files, CI, issue tracker, checkout, posting), invoke `tool-discovery` and record the preferred tool. **Completion:** preferred tools recorded for every capability.
4. **Collect context** — invoke the preferred tool for each capability and store output in `evidence-store`. Fall back when needed and disclose degradation. **Completion:** every capability has evidence or a documented skip/degradation.
5. **Checkout and inspect** — invoke `git-worktree-inspector` to check out the branch and list changed files. Read the files and run targeted checks scoped to changed files. **Completion:** worktree inspected, check results recorded, unintended changes reset.
6. **Synthesize review** — compare changes against ticket scope and project conventions; use `scope-checker` to flag scope drift. Avoid duplicating existing comments. Generate a top-level summary, required/optional inline comments, and confidence. **Completion:** draft review items recorded in state.
7. **Draft review** — write the review draft to `{context_dir}/pr-review/{key}/{key}-review-draft.md` with event, body, and inline comments. **Completion:** report exists and is marked complete.
8. **Review with user** — present the draft, ask for feedback, iterate until explicit confirmation. **Completion:** user confirms the exact draft.
9. **Post or hand back** — if posting confidence is high and the user confirmed, post in one shot. Otherwise, write the exact manual payload to `{context_dir}/pr-review/{key}/{key}-review-payload.md` and explain how to post it. **Completion:** PR has the posted review, or the user has the exact manual payload.

During the workflow, report progress after each phase. Keep progress messages lightweight.

## Incremental output and checkpointing

The skill writes state and reports incrementally. Create a skeleton with `<!-- STATUS: pending -->` markers, fill sections as they complete, and re-read state and report files after every subagent call and after any context compaction. See [references/CHECKPOINTING.md](references/CHECKPOINTING.md).

## Output

Canonical outputs live in `{context_dir}/pr-review/{key}/`:

- `{key}/state.md` — phase, tool selections, confidence, decisions.
- `{key}-review-draft.md` — proposed review text and inline comments.
- `{key}-review-payload.md` — exact manual payload when posting is not used.
- `{key}-decisions.md` — append-only decision log.

See [context-reports](../../../blocks/project/context-reports/SKILL.md) for conventions.

## Confidence and posting gate

- **High confidence:** Direct evidence, tool is configured and tested, line coordinates verified, user has explicitly approved. Posting is allowed.
- **Medium confidence:** Some uncertainty about tool behavior or line coordinates. Do not post; provide the manual payload.
- **Low confidence:** Missing data, untested tool, or conflicting information. Do not post; provide the manual payload and explain gaps.

Always ask for explicit approval before posting, even at high confidence.

## Stop and consult

Stop and ask the user when:

- No PR can be resolved after `identity-resolver`.
- No PR source tool or checkout method is available.
- A configured tool fails to connect (as opposed to being missing or disabled).
- The state file or report is inconsistent.
- A degraded source is about to be accepted without explicit user consent.
- Posting failed and retry confidence is not high.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Workflow](references/WORKFLOW.md)
- [Tool selection](references/TOOL_SELECTION.md)
- [Review draft format](references/REVIEW_DRAFT.md)
- [Posting gate](references/POSTING.md)
- [Checkpointing](references/CHECKPOINTING.md)
- [Config pattern](references/CONFIG_PATTERN.md)
- [Dependencies](references/DEPENDENCIES.md)
- [Validation](references/VALIDATION.md)
