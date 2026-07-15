# Interface

`git-worktree-inspector` exposes one script: `scripts/inspect-worktree.py`.

## Input

JSON on stdin with an `operation` field.

### Common fields

| Field | Required | Description |
|---|---|---|
| `operation` | yes | One of `inspect`, `changed_files`, `cleanup`. |
| `repo` | yes | Path to the git repository. |
| `branch` | yes | Branch or commit to check out. |
| `base` | no | Base branch for diff. Default: `main`. |
| `cwd` | no | Working directory. Default: current directory. |

### `inspect`

```json
{
  "operation": "inspect",
  "repo": "/path/to/repo",
  "branch": "feature/OC-1234",
  "base": "main",
  "commands": [
    {"name": "eslint", "cmd": ["npx", "eslint", "{files}"], "include_files": true}
  ],
  "keep_worktree": false
}
```

- `commands` — list of commands to run. Each command has `name`, `cmd` (array), and `include_files` (boolean). If `include_files` is true and `cmd` contains `{files}`, the placeholder is replaced with the changed files. If `include_files` is true but no placeholder is present, files are appended to the command.
- `keep_worktree` — if true, the worktree is not removed.

### `changed_files`

```json
{
  "operation": "changed_files",
  "repo": "/path/to/repo",
  "branch": "feature/OC-1234",
  "base": "main"
}
```

### `cleanup`

```json
{
  "operation": "cleanup",
  "worktree": "/path/to/worktree"
}
```

## Output

All operations return JSON to stdout.

### `inspect`

```json
{
  "status": "complete",
  "worktree": "/tmp/.../feature-OC-1234",
  "base": "main",
  "base_sha": "abc123...",
  "changed_files": ["src/file.ts", "src/file.test.ts"],
  "results": [
    {
      "name": "eslint",
      "returncode": 0,
      "stdout": "",
      "stderr": "",
      "duration_seconds": 1.2
    }
  ],
  "reset_files": [],
  "clean": true
}
```

### `changed_files`

```json
{
  "status": "found",
  "base": "main",
  "base_sha": "abc123...",
  "changed_files": ["src/file.ts", "src/file.test.ts"]
}
```

### `cleanup`

```json
{
  "status": "removed",
  "worktree": "/tmp/.../feature-OC-1234"
}
```

### Error

```json
{
  "status": "error",
  "errors": ["..."]
}
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Operation succeeded. |
| 1 | Operation failed or a command returned non-zero. |
| 2 | Invalid input. |

## Behavior notes

- In a detached worktree, branch refs from the main repo are not available. To keep diffs reliable, the base ref is resolved to a commit SHA in the main repo before the worktree is created, and the SHA is used for the diff inside the worktree. The `base` field in the output still reports the original ref name, and `base_sha` reports the resolved SHA.
- If a command exits non-zero, the script still runs subsequent commands and records the failure. The final exit code is 1 if any command failed.
- Unintended modifications are reset with `git checkout -- .` after all commands complete.
- The worktree is created under a temporary directory that is a sibling of the main repo by default, or in the system temp directory if the repo path is not writable.
