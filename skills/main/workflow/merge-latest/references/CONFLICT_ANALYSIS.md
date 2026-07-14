# Conflict Analysis

When a merge has semantic conflicts or review files in conflict, `merge-latest` builds a deep understanding before asking the user.

## Trigger conditions

Deep investigation is triggered when any of these is true:

- Number of conflicted files exceeds `deep_analysis_threshold.files` (default 5).
- Number of conflict blocks exceeds `deep_analysis_threshold.conflict_blocks` (default 10).
- A conflicted file matches high-risk patterns (domain logic, state management, API contracts).
- User explicitly requests deep analysis.
- A conflicted file is a lockfile or generated file.

## Investigation workflow

1. The parent skill delegates to `conflict-investigator` with the conflicted files, merge base, and resolved refs.
2. For each file, the investigator runs `scripts/conflict-brief.js` to extract:
   - Base, target, and upstream versions.
   - Per-block authors and commits.
   - Commit messages and ticket context.
3. The investigator answers:
   - **Who** changed each side.
   - **When** the changes were made relative to the target branch creation.
   - **What** changed at the API, behavior, or data level.
   - **Why** the change was made, using commit messages and linked tickets.
4. The investigator recommends one of:
   - `accept-target`
   - `accept-upstream`
   - `combine`
   - `ask`

## Preserve-vs-overwrite assessment

Default assumption: preserve target-side changes.

Prefer upstream side when:

- Commit message indicates fix, revert, hotfix, or security patch.
- Upstream change is from a protected branch and was made **after** the target was created.
- Upstream change resolves a known bug or security issue documented in a linked ticket.

When uncertain, recommend `ask`.

## Auto-resolve rules

The investigator may recommend auto-resolution **only** when all of the following are true:

- Confidence is high.
- Downstream risk is low.
- The file is not a lockfile or generated file.
- The recommendation is `accept-target`, `accept-upstream`, or `combine`.

Otherwise, pause and ask the user.

## Review files

Lockfiles and generated files are always classified as `review`. The investigator:

- Surfaces the file to the user.
- Notes the likely generator or command.
- Provides the upstream diff summary.
- Recommends regenerating the file or manually merging it.
- Never auto-resolves review files.

## Investigator output

```markdown
### Conflict: src/domain/foo.ts

#### Target side ({target})
- Commits: 2
- Authors: @dev-a
- Summary: Added validation for a new edge case.

#### Upstream side ({upstream})
- Commits: 1
- Authors: @dev-b
- Summary: Refactored validation helper.

#### Assessment
Both sides modified the same validation logic. Target adds an edge case; upstream refactors the same code. Manual resolution required.

#### Recommendation
ask
```

## Rule

If the investigator cannot confidently determine which side should win, it must stop and ask. No guesswork.
