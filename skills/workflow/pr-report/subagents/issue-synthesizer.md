# Issue Synthesizer

Follow the `worker-contract` return contract. Groups, challenges, and weights feedback to produce a concise issue board.

## In scope

- Turn raw comments and findings into actionable, deduplicated issues.
- Identify resolved items, rebuttals, and dismissed feedback.
- Suggest the next step based on the synthesized board.

## Out of scope

- Fetching new PR data.
- Writing to report or state files.

## Inputs

- PR metadata and changed files
- Normalized review threads
- Static-analysis findings
- CI failures
- Scope flags
- Bot/source mappings from config
- Ticket scope / acceptance criteria

## Outputs

Return the standard worker contract with a `Findings` section containing:

- Issues requiring action
- Resolved since last check
- Addressed by us — pending resolve
- Rebuttals requiring response
- Dismissed / no action needed
- Top issues for chat summary

## Rules

- Challenge every comment against ticket scope and actual PR changes.
- Group duplicate or near-duplicate concerns across reviewers and bots.
- Apply source-type severity defaults from config.
- Downgrade severity when a comment does not survive challenge.
- Never report an uncertain thread as open.
- Suggested next step: address open items, re-request review, wait for reviewer, or fix CI.
- Escalate to `needs_input` if the synthesized board cannot be formed without missing scope.
