# Configuration pattern for `map-ticket-relationships`

Configuration is passed per-call by the caller rather than read from a dedicated skill config file. The caller may source defaults from its own skill config (e.g., `debrief.yaml`).

## Config keys

| Key | Type | Default | Description |
|---|---|---|---|
| `max_depth` | integer | `1` | How many levels of the relationship graph to expand. Capped at `2` to prevent runaway expansion. |
| `infer_by_file` | boolean | `false` | Whether to infer affected files from path-like strings in the ticket description. |
| `codebase_root` | string | `.` (cwd) | Root directory used for local `git` discovery. |
| `git_remote` | string | `origin` | Remote name to use when resolving remote branches. |

## Example

```yaml
map_ticket_relationships:
  max_depth: 1
  infer_by_file: true
```

## Notes

- This skill does not read its own config file. The caller passes these values directly in the input envelope.
- `max_depth` is enforced by the script; values greater than `2` are clamped to `2`.
