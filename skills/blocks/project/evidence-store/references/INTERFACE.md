# Interface

`evidence-store` exposes one script: `scripts/evidence-store.py`.

## Input

JSON on stdin with an `operation` field.

### Common fields

| Field | Required | Description |
|---|---|---|
| `operation` | yes | One of `append`, `query_latest`, `query_all`, `query_since`, `exists`, `mark_stale`. |
| `context_dir` | no | Project context directory. Default: `.agents/context`. |

### `append`

Append an evidence entry.

```json
{
  "operation": "append",
  "context_dir": ".agents/context",
  "entry": {
    "evidence_id": "...",
    "work_item_type": "pr",
    "work_item_key": "42@owner-repo",
    "capability": "pr-source",
    "source": "github-mcp",
    "source_version": "1.0.0",
    "schema_version": "1.0.0",
    "collected_at": "2026-07-14T10:00:00Z",
    "branch": "feature/OC-1234",
    "commit": "abc1234",
    "confidence": "high",
    "producing_skill": "pr-report",
    "payload": "..."
  }
}
```

Required entry fields: `work_item_type`, `work_item_key`, `capability`, `source`. If `evidence_id` or `collected_at` are omitted, they are generated automatically.

### `query_latest`

Return the latest evidence entry per capability, or for one capability if specified.

```json
{
  "operation": "query_latest",
  "context_dir": ".agents/context",
  "work_item_type": "pr",
  "work_item_key": "42@owner-repo",
  "capability": "pr-source"
}
```

### `query_all`

Return all evidence entries for a work item, optionally filtered by capability.

```json
{
  "operation": "query_all",
  "context_dir": ".agents/context",
  "work_item_type": "pr",
  "work_item_key": "42@owner-repo",
  "capability": "pr-source"
}
```

### `query_since`

Return entries collected after a given timestamp.

```json
{
  "operation": "query_since",
  "context_dir": ".agents/context",
  "work_item_type": "pr",
  "work_item_key": "42@owner-repo",
  "capability": "pr-source",
  "since": "2026-07-14T10:00:00Z"
}
```

### `exists`

Check whether a work item has any evidence.

```json
{
  "operation": "exists",
  "context_dir": ".agents/context",
  "work_item_type": "pr",
  "work_item_key": "42@owner-repo"
}
```

### `mark_stale`

Record that a capability is stale.

```json
{
  "operation": "mark_stale",
  "context_dir": ".agents/context",
  "work_item_type": "pr",
  "work_item_key": "42@owner-repo",
  "capability": "pr-source",
  "reason": "new commit available"
}
```

## Output

All operations return JSON to stdout.

### `append` / `mark_stale`

```json
{
  "status": "appended",
  "evidence_id": "...",
  "path": ".agents/context/evidence/pr/42@owner-repo.timeline.md"
}
```

### `query_latest` / `query_all` / `query_since`

```json
{
  "status": "found" | "not_found",
  "entries": [
    {
      "frontmatter": { ... },
      "body": "..."
    }
  ],
  "count": 1
}
```

### `exists`

```json
{
  "status": "found",
  "exists": true | false,
  "path": "...",
  "count": 0
}
```

### Error

```json
{
  "status": "error",
  "errors": ["..."]
}
```

## Evidence envelope

Every entry has frontmatter and a body:

```yaml
---
evidence_id: <uuid>
work_item_type: ticket | pr | branch | commit
work_item_key: OC-1234
capability: pr-source
source: github-mcp
source_version: 1.0.0
schema_version: 1.0.0
collected_at: 2026-07-14T10:00:00Z
branch: feature/OC-1234
commit: abc1234
confidence: high
producing_skill: pr-report
---

## Payload

The normalized data for this capability.
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Operation succeeded (`found` or `appended`). |
| 1 | Operation returned `not_found` or an error. |
| 2 | Invalid input. |
