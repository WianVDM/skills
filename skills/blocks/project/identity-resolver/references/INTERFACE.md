# Interface

`identity-resolver` exposes one script: `scripts/resolve-identity.py`.

## Input

JSON on stdin with an `operation` field.

### Common fields

| Field | Required | Description |
|---|---|---|
| `operation` | yes | One of `resolve`. |
| `user_input` | no | The user's reference: a number, URL, branch, ticket key, or text. |
| `context_dir` | no | Project context directory. Default: `.agents/context`. |
| `config_dir` | no | Project config directory. Default: `.agents/config`. |
| `repo` | no | Default `owner/repo` if known. |
| `branch` | no | Default branch if known. |
| `work_item_type` | no | Hint: `ticket`, `pr`, `branch`, `commit`. |
| `cwd` | no | Working directory for git detection. Default: current directory. |

### `resolve`

```json
{
  "operation": "resolve",
  "user_input": "https://github.com/owner/repo/pull/42",
  "context_dir": ".agents/context",
  "config_dir": ".agents/config"
}
```

## Resolution order

The resolver tries, in order:

1. **Explicit work-item type** — if `work_item_type` is provided, parse the input accordingly.
2. **Ticket key** — if the input matches `[A-Z][A-Z0-9]*-\d+`, return `type: ticket`.
3. **PR URL** — if the input matches `owner/repo/pull/number`, return `type: pr` with repo and number parsed.
4. **PR number** — if the input is all digits, return `type: pr` using the provided or detected repo.
5. **Commit hash** — if the input is a 40-character hex string or valid git commit, return `type: commit`.
6. **Branch** — if a branch is provided or the current git branch is detectable, return `type: branch`.
7. **Text fallback** — search the input text for a ticket key; if found, return `type: ticket`.
8. **Ask** — if nothing matches, return `status: needs_input`.

## Output

All operations return JSON to stdout.

### `resolve` success

```json
{
  "status": "found",
  "type": "pr",
  "key": "42@owner-repo",
  "repo": "owner/repo",
  "branch": "feature/OC-1234",
  "base": "main",
  "commit": "abc1234",
  "url": "https://github.com/owner/repo/pull/42",
  "project": "OC",
  "source": "url"
}
```

### `resolve` needs input

```json
{
  "status": "needs_input",
  "reason": "could not resolve input to a known work item type",
  "input": "..."
}
```

### Error

```json
{
  "status": "error",
  "errors": ["..."]
}
```

## Output fields

| Field | Description |
|---|---|
| `status` | `found`, `needs_input`, or `error`. |
| `type` | `ticket`, `pr`, `branch`, `commit`. |
| `key` | Stable work-item key for storage and lookup. |
| `repo` | `owner/repo` if known. |
| `branch` | Branch name if known. |
| `base` | Base branch if known. |
| `commit` | Commit SHA if known. |
| `url` | Canonical URL if known. |
| `project` | Ticket project key if type is `ticket`. |
| `source` | How the identity was resolved (`user_input`, `branch`, `text`, `git`, `url`). |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Identity resolved (`found`). |
| 1 | Resolution failed (`needs_input` or `error`). |
| 2 | Invalid input. |
