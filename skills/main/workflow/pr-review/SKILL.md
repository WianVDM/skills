---
name: pr-review
description: Help the user review a pull request by gathering context, reading the PR's existing discussion for what it already settled, inspecting the branch locally in a worktree, running targeted checks on changed files, and drafting a review worth posting — user-facing report separate from the PR-facing draft — then posting only after explicit user approval, with an exact manual payload when posting confidence is not high.
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
  - chainlog
  - git-worktree-inspector
  - scope-checker
  - pr-adapter-contract
  - checkpoint
  - scan-context
  - post-github-pr-review
---

# pr-review

## Purpose

Act as an assistant during a human pull-request review. Gather context, read what the PR's conversation already settled, inspect the changed code locally, run targeted checks, and produce two artifacts: a user-facing report with everything the skill knows, and a PR-facing review draft worth posting. Post only after explicit user approval.

## Skill type

Conductor. It coordinates tools and subagents to prepare and optionally post a review.

## When to use

- The user says `/pr-review`, `review this PR`, `review pull request`, or `help me review`.
- The user provides a PR number, ticket key, branch name, or PR URL.
- The user wants local inspection and targeted checks before drafting a review.
- The user wants a review that adds signal over the PR's existing discussion instead of repeating it.
- The user wants safe posting with a manual fallback when tools are not trustworthy.

## Core contract

Accept a PR identifier, resolve the PR and the tools available, collect context including the full conversation, check out the branch in a worktree, run scoped checks, synthesize findings per the review rubric, produce a report and a draft, confirm with the user, and either post or hand back an exact manual payload.

## In scope

- Resolve PR identity from a number, ticket key, branch name, or URL.
- Resolve the best available tool for every load-bearing capability, model-first, with per-project recipes cached for reuse.
- Collect PR metadata, reviews, inline threads, conversation comments, changed files, CI status, and ticket scope.
- Classify existing discussion into settled, open, and declared intent; never re-flag settled items without user consent.
- Check out the PR branch via `git-worktree-inspector` without disturbing the user's current branch.
- Read changed files in full and run targeted checks scoped to them.
- Synthesize findings per the review rubric, budgeted for signal-to-noise, positioned by reviewer position.
- Produce a user-facing report and a PR-facing draft as separate artifacts.
- Present both, answer open questions with the user, iterate, and require explicit approval before posting.
- Post via the best available tool after approval, or hand back an exact manual payload.
- Record tool selections, confidence levels, and decisions in state.

## Out of scope

- Implementing fixes or writing replies to PR comments.
- Resolving, dismissing, or editing existing threads.
- Approving or merging without explicit user confirmation.
- Posting placeholder reviews, "test" reviews, or partial reviews.
- Running full-project checks that touch files outside the PR scope.
- Posting the user-facing report or any process notes to the PR.

## Workflow

Phases and the workers that execute them. Details in [references/WORKFLOW.md](references/WORKFLOW.md).

| #   | Phase                              | Worker / block                                                          | Completion                                                      |
| --- | ---------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------- |
| 0   | **Intake** (first run per project) | `initialize-skill`                                                      | Style profile resolved and persisted.                           |
| 1   | **Initialize**                     | `detect-project-context`, `tool-discovery`                              | Config exists; PR-source and checkout each have a working path. |
| 2   | **Resolve PR**                     | `identity-resolver`, `artifact-freshness`, `scan-context`               | Identity recorded in state.                                     |
| 3   | **Resolve tools**                  | `tool-discovery` (recipe cache), `token-resolver`                       | Selected tool recorded per capability.                          |
| 4   | **Collect context**                | selected tools, `pr-adapter-contract` shape                             | Every capability has data or a documented skip.                 |
| 5   | **Checkout and inspect**           | `checkout-coordinator` (via `git-worktree-inspector`), `check-selector` | Files read in full; scoped checks recorded.                     |
| 6   | **Synthesize review**              | `review-synthesizer`, `scope-checker`                                   | Findings, settled items, and event recorded.                    |
| 7   | **Draft report and review**        | conductor (report), `review-writer` (draft)                             | Both artifacts written.                                         |
| 8   | **Review with user**               | conductor                                                               | User confirms the exact draft.                                  |
| 9   | **Post or hand back**              | `posting-coordinator` (via `post-github-pr-review` or manual payload)   | Posted, or exact payload delivered.                             |

Report progress after each phase. Keep progress messages lightweight.

## Subagents

- [check-selector](subagents/check-selector.md) — pick targeted checks for the changed files.
- [checkout-coordinator](subagents/checkout-coordinator.md) — worktree, full-file reads, run checks, reset drift.
- [review-synthesizer](subagents/review-synthesizer.md) — findings per the rubric, disposition classification, reviewer position.
- [review-writer](subagents/review-writer.md) — render the PR-facing draft from approved findings.
- [posting-coordinator](subagents/posting-coordinator.md) — payload assembly, coordinate validation, post or manual payload.

## Incremental output and checkpointing

The skill writes state and reports incrementally. Create a skeleton with `<!-- STATUS: pending -->` markers, fill sections as they complete, and re-read state and report files after every subagent call and after any context compaction. Phase checklists and resume state are maintained with the `checkpoint` block. See [references/CHECKPOINTING.md](references/CHECKPOINTING.md).

## Output

Canonical outputs live in `{context_dir}/pr-review/{key}/`:

- `{key}/state.md` — phase, tool selections, confidence, decisions.
- `{key}-review-report.md` — user-facing: findings with evidence, settled items, checks, degradations, open questions.
- `{key}-review-draft.md` — PR-facing: exactly what would be posted.
- `{key}-review-payload.md` — exact manual payload when posting is not used.
- `{key}-decisions.md` — append-only decision log.

See [context-reports](../../../blocks/project/context-reports/SKILL.md) for conventions.

## Confidence and posting gate

Posting requires high confidence and explicit user approval, always. Medium or low confidence hands back the exact manual payload instead. The full rules live in [references/POSTING.md](references/POSTING.md).

## Stop and consult

Stop and ask the user when:

- No PR can be resolved after `identity-resolver`.
- No PR source tool or checkout method is available.
- A configured tool fails to connect (as opposed to being missing or disabled).
- A degraded source is about to be accepted without explicit user consent.
- Gate commands are about to run against an untrusted branch.
- The state file or report is inconsistent.
- Posting failed and retry confidence is not high.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Workflow](references/WORKFLOW.md)
- [Review rubric](references/REVIEW_RUBRIC.md) — what a good review is; governs synthesis and writing.
- [Review report format](references/REVIEW_REPORT.md) — the user-facing artifact.
- [Review draft format](references/REVIEW_DRAFT.md) — the PR-facing artifact.
- [Posting gate](references/POSTING.md)
- [Checkpointing](references/CHECKPOINTING.md)
- [Config pattern](references/CONFIG_PATTERN.md)
- [Chainlog declaration](references/CHAINLOG.md)
- [Dependencies](references/DEPENDENCIES.md)
- [Validation](references/VALIDATION.md)
