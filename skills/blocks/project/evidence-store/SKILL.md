---
name: evidence-store
description: Append-only storage for evidence collected by tools. Lets skills reuse prior work, build reports as views over evidence, and check freshness per capability rather than per report.
version: 1.0.0
invocation: model-invoked
depends:
  - worker-contract
  - context-reports
---

# evidence-store

## Purpose

Store append-only evidence collected by tools so that conductor skills can reuse prior work without trusting stale information. Reports are treated as views over the latest evidence per capability.

## Skill type

Building block. It only reads and writes evidence entries; it does not fetch data or make decisions.

## When to use

A skill should use `evidence-store` when:

- It collects data from multiple sources that may be reused across runs.
- It wants other skills to consume its collected data without re-running the same tools.
- It wants to build reports incrementally from per-capability evidence snapshots.

## In scope

- Append evidence entries to a per-work-item timeline.
- Query the latest evidence entry per capability for a work item.
- Query all evidence entries for a work item, optionally filtered by capability or time.
- Check whether a work item has any evidence.
- Record staleness markers when a capability is known to be stale.

## Out of scope

- Fetching new data from tools or APIs.
- Deciding whether evidence is stale (use `artifact-freshness`).
- Synthesizing reports from evidence.
- Deleting or overwriting evidence entries.

## Core contract

Accepts an evidence entry with work-item identity, capability, source, timestamp, and payload. Appends it to an append-only timeline. Returns the latest evidence per capability when queried.

## Evidence envelope

Every evidence entry has frontmatter and a payload body:

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

Normalized data for this capability.
```

See [references/INTERFACE.md](references/INTERFACE.md) for the full envelope and operation schemas.

## Storage layout

Evidence timelines are stored at:

```text
{context_dir}/evidence/{work_item_type}/{work_item_key_slug}.timeline.md
```

See [references/STORAGE.md](references/STORAGE.md) for details on slugging, file format, and concurrency.

## Operations

- `append` — add an evidence entry.
- `query_latest` — return the latest entry per capability.
- `query_all` — return all entries for a work item, optionally filtered by capability.
- `query_since` — return entries collected after a given timestamp.
- `exists` — check whether a work item has any evidence.
- `mark_stale` — record that a capability is stale.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Interface](references/INTERFACE.md)
- [Storage](references/STORAGE.md)
- [Dependencies](references/DEPENDENCIES.md)
