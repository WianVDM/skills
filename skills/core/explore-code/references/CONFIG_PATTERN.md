# Configuration Pattern

This file documents the configuration keys supported by `explore-code`.

Configuration is passed by the caller in the JSON input, or via a project-level skill config under the `explore_code` key (e.g., `explore_code_max_files`). The script accepts input fields as the authoritative source; config values are defaults.

## Supported keys

| Key | Type | Default | Description |
|---|---|---|---|
| `explore_code_max_files` | integer | `20` | Maximum number of relevant files to return in one invocation. |
| `explore_code_time_box_minutes` | integer | `5` | Target time budget for exploration in minutes. The script stops gracefully when the target is exceeded; it is a soft limit. |
| `explore_code_workspace` | string | `null` | Default monorepo workspace name to scope searches. Can be overridden per call via `workspace`. |
| `explore_code_task_type` | string | `"code"` | Default task type. One of `code`, `ui`, `docs`, `process`. |
| `explore_code_min_relevance` | string | `"Low"` | Minimum relevance threshold to include in results. One of `High`, `Medium`, `Low`. |
| `explore_code_read_limit_lines` | integer | `200` | Maximum number of lines to read from a discovered file when generating a `content_summary`. |

## Example project config

```yaml
explore_code:
  max_files: 20
  time_box_minutes: 5
  workspace: "frontend"
  min_relevance: "Low"
  read_limit_lines: 200
```

Or as flat keys in a shared config:

```yaml
explore_code_max_files: 20
explore_code_time_box_minutes: 5
```

## Resolution order

1. Caller-provided JSON input fields.
2. Skill-specific config key namespace (`explore_code.*`).
3. Flat config keys (`explore_code_*`).
4. Built-in defaults documented above.

## Notes

- `time_box_minutes` is a target, not a hard real-time guarantee. The script checks elapsed time between search batches and stops early when the budget is consumed.
- `max_files` is enforced as a hard cutoff on the returned `relevant_files` list.
- `workspace` is used to restrict `fffind`/`ffgrep` searches to the matching directory. If the workspace does not exist in the project, the script returns `partial` with `missing_files` documented.
