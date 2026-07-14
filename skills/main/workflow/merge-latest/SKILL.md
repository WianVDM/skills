---
name: merge-latest
description: Merge the latest upstream branch into the correct target branch safely. Classifies conflicts as trivial, semantic, or review; resolves only trivial ones automatically; validates the merge with a user-configured command pipeline; and produces a report. Use when the user says '/merge-latest', 'merge latest', 'merge upstream', or wants to sync a feature branch before opening a PR.
version: 1.1.0
invocation: user-invoked
depends:
  - context-reports
  - checkpoint
---

# Merge Latest

## Purpose

Merge the latest upstream branch into the correct target branch safely by classifying conflicts, running a user-confirmed validation pipeline, and producing a report.

## Type

Conductor.

## In scope

- Parse merge arguments and resolve the target and upstream branches.
- Fetch remote state and fast-forward the local target branch when safe.
- Classify conflicts as trivial, semantic, or review.
- Resolve only trivial conflicts automatically.
- Run a user-configured validation command pipeline before completing the merge.
- Pause on semantic conflicts and review-file conflicts for user input.
- Abort the merge if validation fails.
- Produce a merge report and checkpoint state for resumption.
- Resume, inspect, or abort a paused merge.

## Out of scope

- Pushing changes to the remote.
- Resolving semantic conflicts without user input.
- Resolving generated-file or lockfile conflicts automatically.
- Running arbitrary scripts from skill directories without explicit approval.
- Handling non-git version control systems.

## Quality guarantees

- No changes are pushed.
- The target branch is never a protected branch.
- A merge is only committed if the validation pipeline passes.
- Every non-trivial resolution is recorded with a reason.
- State is checkpointed so a paused merge can be resumed.

## When to use

- A feature branch is behind its base branch.
- Before opening a PR.
- When asked to merge latest or merge upstream.
- When a previous merge was paused and needs to continue.
- When checking the status of a paused merge.

## Branch entry

| Branch | Trigger | Outcome |
|---|---|---|
| **merge** | `/merge-latest` (default) | Run the full merge workflow. |
| **preview** | `/merge-latest --preview` | Show the plan without applying changes. |
| **continue** | `/merge-latest --continue` | Resume a paused merge from state. |
| **status** | `/merge-latest --status` | Show current merge state without modifying. |
| **abort** | `/merge-latest --abort` | Abort the in-progress merge and restore state. |

**Completion criterion:** the branch is one of {merge, preview, continue, status, abort} and the user has confirmed or corrected the default.

## Argument handling (merge branch only)

1. Parse tokens with `scripts/parse-args.js`.
2. Supported forms:
   - `/merge-latest` — `to` = current branch, `from` = inferred.
   - `/merge-latest <branch>` — `to` = branch, `from` = inferred.
   - `/merge-latest <to> <from>` — positional target and upstream.
   - `/merge-latest --from <from>` — explicit upstream only.
   - `/merge-latest --to <to> --from <from>` — explicit both.
   - `/merge-latest <to> --from <from>` — mixed.
3. Named arguments override positional values.
4. If the same role is specified both by name and by position, stop and ask.
5. If more than two positional arguments appear, stop and ask.
6. `--stash` is a boolean flag. It is also controlled by config `auto_stash`.

## Resolving target and upstream

1. **Target (`to`)**:
   - Use the argument if provided.
   - Otherwise use the current branch.
2. **Upstream (`from`)**:
   - Use the argument if provided.
   - Otherwise delegate to `branch-researcher` to infer it from history and name similarity.
   - If inference confidence is not high, stop and ask the user.
3. **Remote refs**:
   - Resolve both `to` and `from` to their remote tracking refs where possible (`<remote>/<branch>`).
   - If a remote tracking ref is missing, stop and ask.

See [references/BRANCH_INFERENCE.md](references/BRANCH_INFERENCE.md) for the full inference algorithm.

## Checkout rules

- If the target branch is not the current branch and the working tree is clean, check it out silently.
- If the working tree has modified tracked files and stashing is not approved, stop and ask before doing anything else.
- If the working tree has only untracked files, warn the user but allow continuing.
- If `--stash` is passed or `auto_stash: true`, stash the dirty tree, check out the target branch, and plan to restore the stash after the merge attempt completes or aborts.
- Never check out a protected branch as the target.

## Fetch rules

1. Delegate to `latest-fetcher` to fetch both `<remote>/<to>` and `<remote>/<from>`.
2. If the local target branch is behind its remote tracking ref and the working tree is clean, fast-forward it.
3. If the local target branch has diverged from the remote, stop and ask.
4. Prefer `<remote>/<from>` as the upstream ref for the merge.

## Pre-flight hard stops

STOP and ask the user if any of these are true:

- Modified tracked files exist and stashing is not approved.
- Target branch is a protected branch.
- A merge is already in progress.
- Source and target branches resolve to the same commit.
- Local target branch has diverged from its remote tracking branch.
- The upstream branch cannot be inferred or its remote tracking ref is missing.
- The target branch is already up to date with the upstream (exit early with a message instead).

## Process overview

1. **Parse arguments** — run `scripts/parse-args.js`.
2. **Load config and state** — read `.agents/config/merge-latest.yaml` and `.agents/context/merge-latest/{target}/state.md`.
3. **Resolve target** — checkout if needed.
4. **Fetch latest state** — delegate to `latest-fetcher`.
5. **Resolve upstream** — use explicit value or delegate to `branch-researcher`.
6. **Pre-flight checks** — delegate to `preflight-checker`.
7. **Checkpoint** — record the start of the run.
8. **Reconnaissance** — delegate to `recon-runner` using resolved remote refs.
9. **Backup** — create a backup of current HEAD.
10. **Merge** — attempt merge. If conflicts are expected, use no-commit mode.
11. **Classify conflicts** — delegate to `conflict-classifier`.
12. **Investigate conflicts** — for semantic or review conflicts, delegate to `conflict-investigator`.
13. **Resolve trivial conflicts** — apply only safe resolutions with `scripts/resolve-trivial.js`.
14. **Pause on semantic conflicts** — stop and present context. Do not guess.
15. **Surface review files** — lockfiles and generated files are classified as `review`; ask the user.
16. **Surface binary files** — binary file conflicts are classified as `review`; ask the user.
17. **Run validation pipeline** — delegate to `validation-runner`.
18. **Report** — delegate to `report-writer`.
19. **Update state** — record run, inferences, resolutions, validation result, and decisions.

## Incremental output and checkpointing

For large merges with many conflicts, the skill checkpoints progress in state. The state file tracks:

- Target and upstream refs.
- Inferred base branch history.
- Conflict classification status.
- Applied resolutions.
- Validation status.
- Current phase.

After every subagent returns, and after any context compaction:

1. Update the state file.
2. Update the phase checklist and current focus.
3. Re-read state before deciding the next action.

See [references/CHECKPOINTING.md](references/CHECKPOINTING.md) for phase definitions.

## Recontextualization after compaction

If context compacts mid-merge:

1. Read `.agents/context/merge-latest/{target}/state.md`.
2. Read `.agents/context/merge-latest/{target}-merge-report.md` if it exists.
3. Read the state summary.
4. Resume from the first pending phase.

## Conflict classification

For each conflicted file, classify as:

| Classification | Criteria |
|----------------|----------|
| **Trivial** | Only one side changed the region; non-overlapping additions; whitespace/formatting only. |
| **Semantic** | Both sides changed logic, API, behavior, or deletion state. |
| **Review** | Lockfile, generated file, or binary file; requires timestamp/CI context. |

Trivial conflicts may be resolved automatically. Semantic conflicts pause for user input. Review conflicts are surfaced to the user and never auto-resolved.

See [references/CONFLICT_ANALYSIS.md](references/CONFLICT_ANALYSIS.md) for the investigation workflow.

## Preserve-vs-overwrite policy

Default assumption: preserve target-side changes.

Upstream wins if any of the following is true:

- The upstream commit message indicates a fix, revert, hotfix, or security patch.
- The upstream change is from a protected branch and was made **after** the target branch was created.
- The upstream change resolves a known bug or security issue documented in a linked ticket.

When uncertain, ask.

## Merge validation pipeline

Before completing the merge, run a user-configured validation pipeline. See [references/VALIDATION.md](references/VALIDATION.md) for the full detection and configuration rules.

Detection:

1. On first run, inspect project files to identify candidate validation commands.
2. Present the detected commands to the user with descriptions.
3. Let the user enable, disable, reorder, or edit commands.
4. Persist the final list under `validation.commands`.

Execution:

1. Run each command in order.
2. If any command fails, abort the merge.
3. Record the output of each command in the report.

## Merge vs rebase

Default strategy is **merge**. Rebase is considered only if:

- The user explicitly requests it.
- The branch has not been shared.
- History is clean and linear.
- No semantic conflicts are expected.
- User config `prefer_rebase: true`.

Rebase always requires explicit user approval.

See [references/MERGE_VS_REBASE.md](references/MERGE_VS_REBASE.md).

## Authentication and private remotes

If the remote is private or requires authentication:

1. Prefer SSH keys or credential helpers.
2. If `git fetch` fails with an authentication error, stop and explain.
3. Do not ask for credentials directly; direct the user to configure git authentication.

See [references/CAPABILITIES.md](references/CAPABILITIES.md).

## Output location

```text
.agents/context/merge-latest/
├── {target}-merge-report.md
├── {target}-merge-state.md
└── {target}/
    └── state.md          # canonical state (preferred)
```

The skill also creates backups under:

```text
.agents/context/merge-latest/backups/{target}-{timestamp}/
```

Old backups may be cleaned up periodically.

## Hard stops

Stop and consult the user if:

- Pre-flight checks fail.
- The upstream branch cannot be inferred.
- A semantic conflict is found.
- A review file conflict is found.
- The validation pipeline fails.
- The working tree has unresolved state after a resolution attempt.

## Rules

- **Never push.** Leave all changes local for human review.
- **Abort on validation failure.** A merge that does not validate is a failed merge.
- **No semantic auto-resolution.** If both branches changed the same logic, ask the user.
- **No generated-file auto-resolution.** Lockfiles and generated files are surfaced to the user.
- **No binary-file auto-resolution.** Binary file conflicts are surfaced to the user.
- **One resolution, one reason.** Every trivial resolution is logged with context.
- **Stash is explicit.** Require `--stash` or a clean tree.
- **Protected branches are off-limits.** Refuse to run on configured protected branches.
- **Prefer local git metadata.** Enrich with ticket adapters only when needed for conflict context.
- **Do not drown in context.** Only fetch detailed context for conflicted files.
- **Keep the merge atomic.** Outcomes are: merged-and-validated, aborted, or paused-for-user.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Capability detection](references/CAPABILITIES.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Reports and context](references/CONTEXT_REPORTS.md)
- [Subagent delegation](references/SUBAGENTS.md)
- [Branch inference](references/BRANCH_INFERENCE.md)
- [Conflict analysis](references/CONFLICT_ANALYSIS.md)
- [Merge validation pipeline](references/VALIDATION.md)
- [Merge vs rebase](references/MERGE_VS_REBASE.md)
- [Checkpointing](references/CHECKPOINTING.md)
- [Examples](references/EXAMPLES.md)
- [Ticket adapters](references/TICKET_ADAPTERS.md)
- [Detailed reference](references/REFERENCE.md)
- [Dependencies](references/DEPENDENCIES.md)
