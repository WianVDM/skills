# git-worktree-inspector

Check out a branch or commit in a git worktree and run scoped checks.

## What it does

`git-worktree-inspector` creates an isolated git worktree for a branch or commit, lists the changed files against a base branch, runs a set of commands on those files, detects any unintended file modifications, resets them, and finally cleans up the worktree.

## Directory layout

```text
git-worktree-inspector/
├── SKILL.md
├── README.md
├── config.yaml
├── scripts/
│   └── inspect-worktree.py
├── references/
│   ├── INTERFACE.md
│   ├── WORKFLOW.md
│   └── DEPENDENCIES.md
└── evals/
    └── evals.json
```

## Key conventions

- The user's current branch is never modified.
- Worktrees are created in a temporary directory under the project.
- Changed files are computed as `git diff --name-only base..head`.
- Commands that include `{files}` have the space-separated changed-file list substituted.
- After each command, `git status --porcelain` is checked; unintended modifications are reset with `git checkout -- .` and recorded in the output.
- The worktree is removed after inspection unless `keep_worktree: true` is passed.

## When to maintain or extend this block

- Add new worktree placement strategies.
- Change how changed files are mapped to commands.
- Add support for temporary clones instead of worktrees.

## Shared building blocks

- `detect-project-context` — locate the project root and git repo.
- `worker-contract` — return format if invoked through a subagent.
- `context-reports` — conventions for context directory layout.

## How to update

- Keep worktree lifecycle logic deterministic and testable.
- Preserve the guarantee that the user's current branch is untouched.
