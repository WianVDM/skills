# Storage

## Layout

Evidence timelines are stored at:

```text
{context_dir}/evidence/{work_item_type}/{work_item_key_slug}.timeline.md
```

- `context_dir` — supplied by the caller. Default: `.agents/context`.
- `work_item_type` — one of `ticket`, `pr`, `branch`, `commit`.
- `work_item_key_slug` — the `work_item_key` after slugging for safe filenames.

Each work item has exactly one timeline file. Timelines are append-only.

## Slugging

A work-item key is slugged by replacing filesystem-prohibited characters with an underscore:

```python
re.sub(r'[\\/:*?"<>|]', "_", work_item_key)
```

The slug is used only for the filename. The original key is preserved in the frontmatter so consumers can query by the unmodified key.

## File format

A timeline file is a sequence of markdown entries. Each entry is a YAML frontmatter block followed by a markdown body:

```text
---
evidence_id: 7c9a2b1c...
work_item_type: pr
work_item_key: 42@owner-repo
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

Normalized data for this capability.

---
evidence_id: 8d0b3c2d...
...
```

- Entries are separated by a `---` line that terminates the previous frontmatter and starts the next.
- The body is opaque to the store. It may be any markdown or embedded data (e.g., JSON in a fenced code block).
- The store never rewrites existing entries; it only appends new ones.

## Concurrency

The current storage model uses one append-only file per work item. Writers are expected to be serialized by the calling process. Concurrent writes from independent processes are not guaranteed to be atomic; if a skill needs concurrent writes, it should serialize calls to `evidence-store.py` through a single orchestrator or file lock.

## Growth

Timelines grow indefinitely by design. If a timeline becomes too large for a single file, a future version may introduce sharding (e.g., monthly segments) while preserving the append-only contract. Callers should not assume a fixed file size.

## Staleness markers

A `mark_stale` operation appends an entry with `source: stale-marker` and `stale: true`. The latest entry per capability is still returned by `query_latest`; consumers must inspect the `stale` flag or use `artifact-freshness` to decide whether to trust the evidence.

## Example timeline

```text
.agents/context/evidence/
├── pr/
│   ├── 42@owner-repo.timeline.md
│   └── 101@another-repo.timeline.md
├── ticket/
│   └── OC-1234.timeline.md
└── branch/
    └── feature_OC-1234.timeline.md
```
