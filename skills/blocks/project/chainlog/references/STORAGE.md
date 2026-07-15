# Storage

## Layout

Observation chains are stored at:

```text
{context_dir}/chainlog/{work_item_type}/{work_item_key_slug}.chain.md
```

- `context_dir` — supplied by the caller. Default: `.agents/context`.
- `work_item_type` — one of `ticket`, `pr`, `branch`, `commit`.
- `work_item_key_slug` — the `work_item_key` after slugging for safe filenames.

Each work item has exactly one chain file. Chains are append-only.

## Slugging

A work-item key is slugged by replacing filesystem-prohibited characters with an underscore:

```python
re.sub(r'[\\/:*?"<>|]', "_", work_item_key)
```

The slug is used only for the filename. The original key is preserved in the frontmatter so consumers can query by the unmodified key.

## File format

A chain file is a sequence of markdown entries. Each entry is a YAML frontmatter block followed by a markdown body:

```text
---
observation_id: 7c9a2b1c...
work_item_type: pr
work_item_key: 42@owner-repo
capability: pr-source
source: pr-adapter
source_version: 1.0.0
schema_version: 1.0.0
collected_at: 2026-07-14T10:00:00Z
branch: feature/OC-1234
commit: abc1234
confidence: high
producing_skill: example-skill
---

## Payload

Normalized data for this capability.

---
observation_id: 8d0b3c2d...
...
```

- Entries are separated by a `---` line that terminates the previous frontmatter and starts the next.
- The body is opaque to the store. It may be any markdown or embedded data (e.g., JSON in a fenced code block).
- The store never rewrites existing entries; it only appends new ones.

## Concurrency

The current storage model uses one append-only file per work item. Writers are expected to be serialized by the calling process. Concurrent writes from independent processes are not guaranteed to be atomic; if a skill needs concurrent writes, it should serialize calls to `chainlog.py` through a single orchestrator or file lock.

## Growth

Chains grow indefinitely by design. A future version may introduce linked segments to control file size without breaking the append-only contract. Callers should not assume a fixed file size.

## Staleness markers

A `mark_stale` operation appends an entry with `source: stale-marker` and `stale: true`. The latest entry per capability is still returned by `query_latest`; consumers must inspect the `stale` flag or use `artifact-freshness` to decide whether to trust the observation.

## Example chain

```text
.agents/context/chainlog/
├── pr/
│   ├── 42@owner-repo.chain.md
│   └── 101@another-repo.chain.md
├── ticket/
│   └── OC-1234.chain.md
└── branch/
    └── feature_OC-1234.chain.md
```
