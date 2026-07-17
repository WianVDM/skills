# Interface

`tool-discovery` exposes one script: `scripts/discover-tools.py`.

## Input

JSON on stdin with an `operation` field.

### Common fields

| Field | Required | Description |
|---|---|---|
| `operation` | yes | One of `discover`. |
| `capability` | yes | The capability to discover tools for. |
| `config_dir` | no | Project config directory. Default: `.agents/config`. |
| `preference` | no | Tool preference: `auto`, `mcp`, `cli`, `api`, `harness`, `manual`. Default: `auto`. |
| `registry` | no | Path to a custom capability registry YAML file. Default: bundled registry. |

### `discover`

```json
{
  "operation": "discover",
  "capability": "pr-source",
  "config_dir": ".agents/config",
  "preference": "auto"
}
```

## Output

All operations return JSON to stdout.

### `discover`

```json
{
  "status": "found",
  "capability": "pr-source",
  "tools": [
    {
      "name": "github-mcp",
      "category": "mcp",
      "available": true,
      "confidence": "high",
      "detail": "MCP keywords github matched"
    }
  ]
}
```

### Error

```json
{
  "status": "error",
  "errors": ["..."]
}
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
| `high` | Tool is configured and prerequisites are present. |
| `medium` | Tool is present but may need additional setup. |
| `low` | Tool is a fallback or lacks direct detection. |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Operation succeeded. |
| 1 | Operation returned an error or no tools were found. |
| 2 | Invalid input. |
