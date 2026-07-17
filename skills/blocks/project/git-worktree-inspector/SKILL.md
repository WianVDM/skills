---
name: git-worktree-inspector
description: Check out a branch or commit in a git worktree, inspect changed files, run scoped checks, and clean up without disturbing the user's current branch.
invocation: model-invoked
---

# git-worktree-inspector

## Purpose

Provide a safe, isolated workspace for inspecting a PR branch and running targeted checks against the changed files. The user's current branch is never modified.

## Skill type

Building block. It only prepares the worktree and runs commands; it does not interpret results or post reviews.

## When to use

A conductor needs to verify a PR branch locally without switching the user's current branch. Use `git-worktree-inspector` when:

- The review workflow requires checking out the PR branch.
- Scoped checks (lint, type-check, tests) need to run on changed files only.
- The current branch must remain untouched.

## In scope

- Create a git worktree for a branch or commit.
- List changed files between the worktree head and a base branch.
- Run a configured list of commands in the worktree.
- Detect and reset unintended file modifications caused by checks.
- Remove the worktree when done.

## Out of scope

- Interpreting check results or deciding whether they block the PR.
- Posting reviews or comments.
- Installing tools or dependencies without explicit user approval.
- Persisting state between runs.

## Core contract

Accept a repo path, branch or commit, and base branch. Return the worktree path, changed files, and command results. Unintended modifications are detected and reset.

## Operations

- `inspect` — create a worktree, list changed files, run commands, reset unintended changes, and return results.
- `changed_files` — list files changed between base and head.
- `cleanup` — remove a worktree created by this block.

## Input

```json
{
  "operation": "inspect",
  "repo": "/path/to/repo",
  "branch": "feature/OC-1234",
  "base": "main",
  "commands": [
    {
      "name": "eslint",
      "cmd": ["npx", "eslint", "{files}"],
      "include_files": true
    }
  ]
}
```

## Output

```json
{
  "status": "complete",
  "worktree": "/path/to/repo/.git/worktrees/...",
  "changed_files": ["src/file.ts"],
  "results": [
    { "name": "eslint", "returncode": 0, "stdout": "...", "stderr": "" }
  ],
  "reset_files": ["src/file.ts"],
  "clean": true
}
```

See [references/INTERFACE.md](references/INTERFACE.md) for the full schema.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Interface](references/INTERFACE.md)
- [Workflow](references/WORKFLOW.md)
- [Dependencies](references/DEPENDENCIES.md)
