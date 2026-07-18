# Issue Synthesizer

Follow the `worker-contract` return contract. Groups, challenges, and weights feedback to produce a concise issue board.

## In scope

- Consume normalized data produced by the `normalize-observation` worker in the `pr-adapter-contract` shapes.
- Turn normalized comments and findings into actionable, deduplicated issues.
- Identify resolved items, rebuttals, and dismissed feedback.
- Generate a task list when `pr-report.task_list.enabled` is true.
- Suggest the next step based on the synthesized board.

## Out of scope

- Fetching new PR data.
- Writing to report or state files.

## Inputs

- Normalized PR metadata, changed files, reviews, and threads (from `normalize-observation`)
- Normalized conversation comments (from `normalize-observation`)
- Normalized CI failures (from `normalize-observation`)
- Normalized static-analysis findings (from `normalize-observation`)
- Normalized ticket scope / acceptance criteria (from `normalize-observation`)
- Scope flags (from the `scope-checker` block)
- Bot/source mappings from config
- `pr-report.task_list.enabled` flag

## Outputs

Return the standard worker contract with a `Findings` section containing:

- Issues requiring action
- Resolved since last check
- Addressed by us — pending resolve
- Rebuttals requiring response
- Dismissed / no action needed
- Top issues for chat summary
- Generated task list (when enabled)

## Rules

- Challenge every comment against ticket scope and actual PR changes.
- Group duplicate or near-duplicate concerns across reviewers and bots.
- Apply source-type severity defaults from config.
- Downgrade severity when a comment does not survive challenge.
- Never report an uncertain thread as open.
- Suggested next step: address open items, re-request review, wait for reviewer, or fix CI.
- Escalate to `needs_input` if the synthesized board cannot be formed without missing scope.
