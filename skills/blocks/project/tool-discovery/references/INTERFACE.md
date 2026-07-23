# Interface

`tool-discovery` exposes one script: `scripts/discover-tools.py`.

## Input

JSON on stdin with an `operation` field.

### Common fields

| Field | Required | Description |
|---|---|---|
| `operation` | yes | One of `discover`, `cache-get`, `cache-put`, `cache-invalidate`. |
| `capability` | yes | The capability to operate on. |
| `config_dir` | no | Project config directory. Default: `.agents/config`. |

### `discover`

```json
{
  "operation": "discover",
  "capability": "pr-source",
  "config_dir": ".agents/config",
  "project_root": ".",
  "preference": "auto",
  "probe": true,
  "search_scope": "all",
  "registry": "path/to/custom-registry.yaml"
}
```

| Field | Default | Description |
|---|---|---|
| `project_root` | `.` | Project root for platform detection and project-level config search. |
| `preference` | `auto` | Tool preference: `auto`, `mcp`, `cli`, `api`, `harness`, `manual`. |
| `probe` | `false` | Run auth probes (`gh auth status`, `glab auth status`) for detected CLIs. |
| `search_scope` | `all` | `all` searches home + project locations; `project` restricts to project locations. |
| `registry` | bundled | Path to a custom capability registry YAML file. |

### `cache-get`

```json
{"operation": "cache-get", "capability": "pr-source", "config_dir": ".agents/config"}
```

### `cache-put`

```json
{
  "operation": "cache-put",
  "capability": "pr-source",
  "config_dir": ".agents/config",
  "entry": {
    "tool": "github-mcp",
    "platform": "github",
    "derived_at": "2026-07-20T14:32:00Z",
    "validated": true,
    "coverage": "complete",
    "missing": [],
    "steps": [{"call": "github_get_pull_request", "yields": "metadata"}],
    "revalidate": "github_get_pull_request on the current PR"
  }
}
```

### `cache-invalidate`

```json
{"operation": "cache-invalidate", "capability": "pr-source", "config_dir": ".agents/config"}
```

## Output

All operations return JSON to stdout.

### `discover`

```json
{
  "status": "found",
  "capability": "pr-source",
  "config_dir": "...",
  "platform": "github",
  "tools": [
    {
      "name": "github-mcp",
      "category": "mcp",
      "available": true,
      "confidence": "high",
      "detail": "MCP keywords github matched"
    },
    {
      "name": "gh-cli",
      "category": "cli",
      "available": true,
      "confidence": "high",
      "detail": "binary gh found on PATH; authenticated",
      "auth": "authenticated"
    }
  ]
}
```

- `platform` is detected from the git origin remote: `github`, `gitlab`, `azure`, `bitbucket`, or `unknown`.
- `auth` appears on CLI tools when `probe` is true: `authenticated`, `not_authenticated`, or `unknown`. An unauthenticated CLI is downgraded to `low` confidence.

### `cache-get`

```json
{"status": "found", "capability": "pr-source", "entry": {...}}
```

`not_found` when no entry exists.

### `cache-put` / `cache-invalidate`

```json
{"status": "written", "capability": "pr-source", "path": ".../tool-recipes.yaml"}
{"status": "invalidated", "capability": "pr-source"}
```

### Error

```json
{"status": "error", "errors": ["..."]}
```

## Tool category ranking

When `preference` is `auto`, the default ranking order is:

1. `mcp` (highest confidence when configured)
2. `cli`
3. `api`
4. `harness`
5. `manual` (lowest confidence, always available)

A user preference overrides the ranking for tools that match the preferred category. For example, `preference: cli` moves available CLI tools to the top of the list.

## Confidence levels

| Level | Meaning |
|---|---|
| `high` | Tool is configured and prerequisites are present (authenticated, when probed). |
| `medium` | Tool is present but may need additional setup, or presence is unverifiable. |
| `low` | Tool is a fallback, lacks direct detection, or failed an auth probe. |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Operation succeeded (`found`, `written`, `invalidated`). |
| 1 | Operation returned an error, `not_found`, or no tools found. |
| 2 | Invalid input. |
