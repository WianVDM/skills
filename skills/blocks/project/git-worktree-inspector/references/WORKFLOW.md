# Workflow

## Operation: `inspect`

1. **Validate inputs** — ensure `repo` and `branch` are provided. Resolve `repo` to an absolute path. Verify it is a git repository.
2. **Resolve base branch** — use the provided `base` or fall back to `main`. If `main` does not exist, try `master`.
3. **Create worktree** — run `git worktree add --checkout <temp-path> <branch>` in the repo. The path includes a sanitized branch name and a short random suffix to avoid collisions.
4. **List changed files** — run `git diff --name-only base..HEAD` in the worktree.
5. **Run commands** — for each command in `commands`:
   - Substitute `{files}` with the changed files if `include_files` is true.
   - If `include_files` is true and no placeholder exists, append the changed files to the command.
   - Run the command in the worktree directory.
   - Capture stdout, stderr, and return code.
6. **Detect unintended modifications** — run `git status --porcelain` in the worktree. Collect modified files.
7. **Reset unintended modifications** — run `git checkout -- .` in the worktree. Record the reset files in the output.
8. **Clean up** — if `keep_worktree` is false, run `git worktree remove <temp-path>`.
9. **Return results**.

## Operation: `changed_files`

1. Validate inputs and resolve the repo path.
2. Create a worktree for the branch.
3. Run `git diff --name-only base..HEAD`.
4. Return the list of changed files.
5. Clean up the worktree.

## Operation: `cleanup`

1. Validate that `worktree` is provided.
2. Run `git worktree remove <worktree>` if it exists and is a registered worktree.
3. Return the removal status.

## Safety rules

- Never create a worktree inside the current working tree of the main repo.
- Never modify the main repo's HEAD or current branch.
- Always reset unintended modifications before returning.
- Always remove the worktree unless `keep_worktree: true` is passed.
