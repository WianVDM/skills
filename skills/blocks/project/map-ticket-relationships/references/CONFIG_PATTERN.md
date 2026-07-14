# Configuration pattern for `map-ticket-relationships`

Configuration is passed per-call by the caller rather than read from a dedicated skill config file. The caller may source defaults from its own skill config (e.g., `debrief.yaml`).

## Config keys

| Key | Type | Default | Description |
|---|---|---|---|
| `infer_by_file` | boolean | `false` | Whether to infer affected files from path-like strings in the ticket description. Candidates are validated against the filesystem under `codebase_root` when possible. |
| `codebase_root` | string | `.` (cwd) | Root directory used for local `git` discovery and affected-file validation. |

## Example

```yaml
map_ticket_relationships:
  infer_by_file: true
```

## Notes

- This skill does not read its own config file. The caller passes these values directly in the input envelope.
- This version does not expand the graph recursively. Multi-level relationship expansion is deferred to a future version that calls tracker APIs.
