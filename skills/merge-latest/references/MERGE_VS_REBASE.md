# Merge vs Rebase

`merge-latest` defaults to merge. Rebase is considered only in specific circumstances and always requires explicit user approval.

## Default: merge

Merge is preferred because:

- It preserves history.
- It is safer for shared branches.
- It makes conflict resolution reversible via `git merge --abort`.
- It creates a clear merge commit.

## When rebase may be suggested

Rebase is considered only if all of these are true:

1. The user has set `prefer_rebase: true` in config, or explicitly asks for rebase.
2. The branch has not been pushed to a shared remote (or user confirms force-push is acceptable).
3. The branch history is linear and clean.
4. No semantic conflicts are expected.
5. The target branch is a personal feature branch.

## User approval

Even when rebase is suggested, the skill must ask for explicit confirmation before proceeding. The prompt should explain why rebase is being considered and the risks.

## If rebase is chosen

1. Create a backup first.
2. Run `git rebase {upstream}`.
3. Resolve conflicts using the same trivial/semantic classification.
4. Validate with build after rebase completes.
5. Report result.

## If rebase fails

- If conflicts occur, pause and ask the user.
- If the user wants to abort, run `git rebase --abort` and restore from backup.
