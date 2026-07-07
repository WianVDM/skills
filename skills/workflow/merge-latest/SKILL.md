---
name: merge-latest
description: Merge the latest upstream branch into the correct target branch safely. Understands branch relationships, fetches remote state, deeply investigates conflicts, and stops when uncertain. Use when the user says '/merge-latest', 'merge latest', 'merge upstream', or wants to sync a feature branch before opening a PR.
argument-hint: "optional target branch, optional upstream branch, optional --stash"
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "1.0.0"
---

# Merge Latest

You are a **careful merge operator**. Your job is to bring the latest upstream changes into the right target branch without silently destroying work. You prefer aborting a merge over guessing at a semantic conflict. Every resolution you make is recorded with a reason.

## Skill type

Workflow skill. It modifies the working tree and produces a report. It does not recommend next skills.

## When to use

- A feature branch is behind its base branch.
- Before opening a PR.
- When asked to merge latest.
- When conflicts need to be classified and only trivial ones resolved safely.

## Quick start

```/merge-latest```                                     # merge inferred base into current branch
```/merge-latest SHB-317```                             # merge inferred base into SHB-317
```/merge-latest SHB-317 origin/development```          # explicit target and upstream
```/merge-latest --from origin/main```                  # merge origin/main into current branch
```/merge-latest --to SHB-317 --from origin/main```     # explicit both sides
```/merge-latest --stash```                             # allow stashing dirty work tree

## Argument handling

1. Parse tokens with `scripts/parse-args.js`.
2. Supported forms:
   - `/merge-latest` — `to` = current branch, `from` = inferred.
   - `/merge-latest <branch>` — `to` = branch, `from` = inferred.
   - `/merge-latest <to> <from>` — positional target and upstream.
   - `/merge-latest --from <from>` — explicit upstream only.
   - `/merge-latest --to <to> --from <from>` — explicit both.
   - `/merge-latest <to> --from <from>` — mixed.
3. Named arguments override positional values.
4. If the same role is specified both by name and position, stop and ask.
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
- If the working tree is dirty and stashing is not approved, stop and ask before doing anything else.
- If `--stash` is passed or `auto_stash: true`, stash the dirty tree, check out the target branch, and plan to restore the stash after the merge attempt completes or aborts.
- Never check out a protected branch as the target.

## Fetch rules

1. Delegate to `latest-fetcher` to fetch both `<remote>/<to>` and `<remote>/<from>`.
2. If the local target branch is behind its remote tracking ref and the working tree is clean, fast-forward it.
3. If the local target branch has diverged from the remote, stop and ask.
4. Prefer `<remote>/<from>` as the upstream ref for the merge.

## Pre-flight hard stops

STOP and ask the user if any of these are true:

- Working tree is dirty and stashing is not approved.
- Target branch is a protected branch.
- A merge is already in progress.
- Source and target branches resolve to the same commit.
- Local target branch has diverged from its remote tracking branch.
- The upstream branch cannot be inferred or its remote tracking ref is missing.

## Process overview

1. **Parse arguments** — run `scripts/parse-args.js`.
2. **Load config and state** — read `.agents/config/merge-latest.yaml` and `.agents/context/merge-latest/{target}/state.md`.
3. **Resolve target** — checkout if needed.
4. **Fetch latest state** — delegate to `latest-fetcher`.
5. **Resolve upstream** — use explicit value or delegate to `branch-researcher`.
6. **Pre-flight checks** — delegate to `preflight-checker`.
7. **Checkpoint** — ask `checkpoint-manager` to record the start of the run.
8. **Reconnaissance** — delegate to `recon-runner` using resolved remote refs.
9. **Backup** — create a backup of current HEAD.
10. **Merge** — attempt merge. If conflicts are expected, use no-commit mode.
11. **Classify conflicts** — delegate to `conflict-classifier`.
12. **Investigate conflicts** — for semantic or review conflicts, delegate to `conflict-investigator`.
13. **Resolve trivial conflicts** — apply only safe resolutions with `scripts/resolve-trivial.js`.
14. **Pause on semantic conflicts** — stop and present context. Do not guess.
15. **Surface review files** — lockfiles and generated files are classified as `review`; ask the user.
16. **Build validation** — delegate to `build-validator`. If it fails, abort the merge.
17. **Report** — delegate to `report-writer`.
18. **Update state** — record run, inferences, resolutions, build result, and decisions.

## Incremental output and checkpointing

For large merges with many conflicts, the skill checkpoints progress in state. The state file tracks:

- Target and upstream refs.
- Inferred base branch history.
- Conflict classification status.
- Applied resolutions.
- Build status.
- Current phase.

After every subagent returns, and after any context compaction:

1. Update the state file.
2. Ask `checkpoint-manager` to update the phase checklist and current focus.
3. Re-read state before deciding the next action.

See [references/CHECKPOINTING.md](references/CHECKPOINTING.md) for phase definitions.

## Recontextualization after compaction

If context compacts mid-merge:

1. Read `.agents/context/merge-latest/{target}/state.md`.
2. Read `.agents/context/merge-latest/{target}-merge-report.md` if it exists.
3. Ask `checkpoint-manager` for status summary.
4. Resume from the first pending phase.

## Conflict classification

For each conflicted file, classify as:

| Classification | Criteria |
|----------------|----------|
| **Trivial** | Only one side changed the region; non-overlapping additions; whitespace/formatting only. |
| **Semantic** | Both sides changed logic, API, behavior, or deletion state. |
| **Review** | Lockfile or generated file; requires timestamp/CI context. |

Trivial conflicts may be resolved automatically. Semantic conflicts pause for user input. Review conflicts are surfaced to the user and never auto-resolved.

See [references/CONFLICT_ANALYSIS.md](references/CONFLICT_ANALYSIS.md) for the investigation workflow.

## Preserve-vs-overwrite policy

Default assumption: preserve target-side changes.

Upstream wins if any of the following is true:

- The upstream commit message indicates a fix, revert, hotfix, or security patch.
- The upstream change is from a protected branch and was made **after** the target branch was created.
- The upstream change resolves a known bug or security issue documented in a linked ticket.

When uncertain, ask.

## Build validation

Run the project build after trivial resolutions and before completing the merge. If the build fails, abort the merge and report the failure.

Build command detection:

1. Use `build_command` from config if set.
2. Auto-detect from project files (`package.json`, `Makefile`, `build.gradle`, `pom.xml`, etc.).
3. Ask the user if detection fails.
4. Persist the resolved command in config.

See [references/BUILD_SYSTEMS.md](references/BUILD_SYSTEMS.md).

## Merge vs rebase

Default strategy is **merge**. Rebase is considered only if:

- The user explicitly requests it.
- The branch has not been shared.
- History is clean and linear.
- No semantic conflicts are expected.
- User config `prefer_rebase: true`.

Rebase always requires explicit user approval.

See [references/MERGE_VS_REBASE.md](references/MERGE_VS_REBASE.md).

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
- The build fails.
- The working tree has unresolved state after a resolution attempt.

## Rules

- **Never push.** Leave all changes local for human review.
- **Abort on build failure.** A merge that does not build is a failed merge.
- **No semantic auto-resolution.** If both branches changed the same logic, ask the user.
- **No generated-file auto-resolution.** Lockfiles and generated files are surfaced to the user.
- **One resolution, one reason.** Every trivial resolution is logged with context.
- **Stash is explicit.** Require `--stash` or a clean tree.
- **Protected branches are off-limits.** Refuse to run on configured protected branches.
- **Prefer local git metadata.** Enrich with ticket adapters only when needed for conflict context.
- **Do not drown in context.** Only fetch detailed context for conflicted files.
- **Keep the merge atomic.** Outcomes are: merged-and-built, aborted, or paused-for-user.

## References

- [Capability detection](references/CAPABILITIES.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Reports and context](references/CONTEXT_REPORTS.md)
- [Subagent delegation](references/SUBAGENTS.md)
- [Branch inference](references/BRANCH_INFERENCE.md)
- [Conflict analysis](references/CONFLICT_ANALYSIS.md)
- [Build systems](references/BUILD_SYSTEMS.md)
- [Merge vs rebase](references/MERGE_VS_REBASE.md)
- [Checkpointing](references/CHECKPOINTING.md)
- [Detailed reference](references/REFERENCE.md)
- [Examples](references/EXAMPLES.md)
- [Validation](references/VALIDATION.md)
- [Ticket adapters](references/TICKET_ADAPTERS.md)

## Out of scope

- Recommending the next skill to run.
- Pushing changes.
- Resolving semantic conflicts without user input.
- Resolving generated-file or lockfile conflicts automatically.
