---
name: chainlog
description: Append-only storage for observations collected by tools. Lets skills reuse prior work, build reports as views over observations, and check freshness per capability rather than per report.
version: 1.0.0
invocation: model-invoked
depends:
  - worker-contract
  - context-reports
---

# chainlog

## Purpose

Store append-only observations collected by tools so that skills can reuse prior work without trusting stale information. Reports are treated as views over the latest observations per capability.

## Skill type

Building block. It only reads and writes observation entries; it does not fetch data or make decisions.

## When to use

A skill should use `chainlog` when:

- It collects data from multiple sources that may be reused across runs.
- It wants other skills to consume its collected data without re-running the same tools.
- It wants to build reports incrementally from per-capability observation snapshots.

## In scope

- Append observation entries to a per-work-item chain.
- Query the latest observation entry per capability for a work item.
- Query all observation entries for a work item, optionally filtered by capability or time.
- Check whether a work item has any observations.
- Record staleness markers when a capability is known to be stale.

## Out of scope

- Fetching new data from tools or APIs.
- Deciding whether observations are stale (use `artifact-freshness`).
- Synthesizing reports from observations.
- Deleting or overwriting observation entries.

## Core contract

Accepts an observation entry with work-item identity, capability, source, timestamp, and payload. Appends it to an append-only chain. Returns the latest observation per capability when queried.

## Observation envelope

Every observation entry has frontmatter and a payload body:

```yaml
---
observation_id: <uuid>
work_item_type: ticket | pr | branch | commit
work_item_key: OC-1234
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
```

See [references/INTERFACE.md](references/INTERFACE.md) for the full envelope and operation schemas.

## Storage layout

Observation chains are stored at:

```text
{context_dir}/chainlog/{work_item_type}/{work_item_key_slug}.chain.md
```

See [references/STORAGE.md](references/STORAGE.md) for details on slugging, file format, and concurrency.

## Operations

- `append` — add an observation entry.
- `query_latest` — return the latest entry per capability.
- `query_all` — return all entries for a work item, optionally filtered by capability.
- `query_since` — return entries collected after a given timestamp.
- `exists` — check whether a work item has any observations.
- `mark_stale` — record that a capability is stale.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Interface](references/INTERFACE.md)
- [Storage](references/STORAGE.md)
- [Dependencies](references/DEPENDENCIES.md)
