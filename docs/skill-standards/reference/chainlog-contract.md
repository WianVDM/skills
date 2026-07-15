# Chainlog contract

This document defines the machine-readable contract for the [`chainlog`](../patterns/chainlog.md) pattern. It specifies the storage model, observation envelope, operations, and adapter requirements that any `chainlog` implementation must satisfy.

---

## Storage model

The default `chainlog` adapter stores observations as a chain of linked segments. Implementations that use a different backend must still expose the same logical model.

### Linked segments

A chain is a sequence of segments for one work item. Each segment holds a consecutive slice of observations. When a segment reaches its threshold, the adapter starts a new segment and links it to the previous one.

Old segments are read-only. Only the head segment accepts new observations. This preserves the append-only property while controlling file size.

### File layout (default adapter)

```text
{context_dir}/chainlog/
├── pr/
│   ├── 42@owner-repo.head
│   ├── 42@owner-repo.000.chain.md
│   └── 42@owner-repo.001.chain.md
├── ticket/
│   ├── OC-1234.head
│   ├── OC-1234.000.chain.md
│   └── OC-1234.001.chain.md
└── branch/
    └── feature-OC-1234-fix.head
    └── feature-OC-1234-fix.000.chain.md
```

The exact layout is an implementation detail of the default adapter. Other adapters may use different physical layouts, but they must expose the same logical work item, segment, and observation model.

### Segment frontmatter

Each segment begins with metadata that links it to the chain:

```yaml
---
segment_id: 42@owner-repo.001
work_item_type: pr
work_item_key: 42@owner-repo
previous_segment: 42@owner-repo.000
first_observation_at: 2026-07-14T10:00:00Z
last_observation_at: 2026-07-14T11:30:00Z
entry_count: 12
schema_version: 1.0.0
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `segment_id` | yes | Stable identifier for this segment. |
| `work_item_type` | yes | `ticket`, `pr`, `branch`, `commit`, or another bounded type. |
| `work_item_key` | yes | Stable identifier for the work item. |
| `previous_segment` | no | Identifier of the previous segment; omitted for the first segment. |
| `first_observation_at` | yes | ISO 8601 timestamp of the first observation in the segment. |
| `last_observation_at` | yes | ISO 8601 timestamp of the last observation in the segment. |
| `entry_count` | yes | Number of observations in the segment. |
| `schema_version` | yes | Version of the segment envelope schema. |

### Observation envelope

Each observation has frontmatter and a body:

```yaml
---
evidence_id: <uuid>
work_item_type: pr
work_item_key: 42@owner-repo
capability: pr-source
source: pr-adapter
source_version: 1.0.0
schema_version: 1.0.0
collected_at: 2026-07-14T10:00:00Z
branch: feature/OC-1234-fix
commit: abc1234def5678
confidence: high
producing_skill: example-skill
related_report: .agents/context/{report-type}/42@owner-repo.md
---

## Payload

Normalized data for this capability, defined by the capability contract.
```

| Field | Required | Description |
|-------|----------|-------------|
| `evidence_id` | yes | UUID for this observation. Generated if omitted. |
| `work_item_type` | yes | `ticket`, `pr`, `branch`, `commit`, or another bounded type. |
| `work_item_key` | yes | Stable identifier for the work item. |
| `capability` | yes | The capability category. |
| `source` | yes | The tool, adapter, or skill that produced the observation. |
| `source_version` | yes | Version of the source tool or adapter. |
| `schema_version` | yes | Version of the observation envelope. |
| `collected_at` | yes | ISO 8601 timestamp when the observation was collected. Generated if omitted. |
| `branch` | no | The branch the observation applies to, if relevant. |
| `commit` | no | The commit the observation applies to, if relevant. |
| `confidence` | yes | `high`, `medium`, or `low`. |
| `producing_skill` | no | The skill that produced the observation. |
| `related_report` | no | Path to a view generated from this observation. |

The payload body is opaque to the chainlog. Its schema is defined by the relevant capability contract.

---

## Operations

A `chainlog` implementation must expose these operations. The exact invocation mechanism depends on the harness, but the JSON contract is fixed.

### Common input fields

| Field | Required | Description |
|-------|----------|-------------|
| `operation` | yes | One of the operations below. |
| `context_dir` | no | Project context directory. Default: `.agents/context`. |

### `append`

Add a new observation to the head segment for a work item.

**Input:**

```json
{
  "operation": "append",
  "context_dir": ".agents/context",
  "entry": {
    "work_item_type": "pr",
    "work_item_key": "42@owner-repo",
    "capability": "pr-source",
    "source": "pr-adapter",
    "source_version": "1.0.0",
    "schema_version": "1.0.0",
    "collected_at": "2026-07-14T10:00:00Z",
    "branch": "feature/OC-1234-fix",
    "commit": "abc1234def5678",
    "confidence": "high",
    "producing_skill": "example-skill",
    "payload": "..."
  }
}
```

Required entry fields: `work_item_type`, `work_item_key`, `capability`, `source`. If `evidence_id` or `collected_at` are omitted, the implementation generates them.

**Output:**

```json
{
  "status": "appended",
  "evidence_id": "...",
  "path": ".agents/context/chainlog/pr/42@owner-repo.001.chain.md"
}
```

### `query_latest`

Return the latest observation per capability, or for one capability if specified.

**Input:**

```json
{
  "operation": "query_latest",
  "context_dir": ".agents/context",
  "work_item_type": "pr",
  "work_item_key": "42@owner-repo",
  "capability": "pr-source"
}
```

**Output:**

```json
{
  "status": "found",
  "entries": [
    {
      "frontmatter": { ... },
      "body": "..."
    }
  ],
  "count": 1
}
```

### `query_all`

Return all observations for a work item, optionally filtered by capability.

**Input:**

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

Return observations collected after a given timestamp.

**Input:**

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

Check whether a work item has any observations.

**Input:**

```json
{
  "operation": "exists",
  "context_dir": ".agents/context",
  "work_item_type": "pr",
  "work_item_key": "42@owner-repo"
}
```

**Output:**

```json
{
  "status": "found",
  "exists": true,
  "path": "...",
  "count": 12
}
```

### `mark_stale`

Append a marker indicating that a capability is stale.

**Input:**

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

**Output:**

```json
{
  "status": "appended",
  "evidence_id": "...",
  "path": "..."
}
```

### Error response

All operations return a consistent error shape on failure:

```json
{
  "status": "error",
  "errors": ["..."]
}
```

---

## Storage adapter contract

A `chainlog` storage adapter is the backend that implements the operations above. The default adapter writes linked markdown segments. Other adapters may target graph databases, vector stores, or harness memory.

Every adapter must satisfy:

- **Append-only semantics.** Observations are never deleted, modified, or overwritten.
- **Immutable history.** Once written, an observation cannot change.
- **Same operation contract.** All operations accept the same input and return the same output shape.
- **Same envelope shape.** Observations and segments use the same frontmatter fields regardless of backend.
- **Default fallback.** If the adapter fails, the implementation must be able to fall back to the default file adapter without losing the append-only guarantee.

Adapters are discovered through the same [`tooling-awareness`](../fundamentals/architecture/tooling-awareness.md) rules as any other capability.

---

## Schema versioning

The observation envelope and the segment envelope each have a `schema_version`. The payload schema is governed by the capability contract.

An implementation must:

- Store observations with the `schema_version` provided by the producer.
- Return the `schema_version` to consumers unchanged.
- Not reject old observations because of a newer `schema_version`.

Consumers must check `schema_version` and `source_version` before assuming a payload shape.

---

## Security

- Do not store secret values in observations or segment metadata.
- Scope observations to the project context directory unless the storage adapter is explicitly cross-project.
- A consumer must not trust an observation solely because it exists in the chainlog. It must evaluate source, confidence, and freshness.
- Append-only semantics prevent tampering with history, but they do not prevent poisoned observations. Consumers must validate payload content.

---

## Related

- [`chainlog` pattern](../patterns/chainlog.md) — the architectural rationale and producer/consumer rules.
- [`context-reports` pattern](../patterns/context-reports.md) — reports are views that may be generated from chainlog observations.
- [`stateful` pattern](../patterns/stateful.md) — private working state versus shared chainlog observations.
- [`tooling-awareness`](../fundamentals/architecture/tooling-awareness.md) — discovering chainlog storage adapters.
