# Chainlog

A **chainlog** is a shared, append-only ledger of observations that skills produce and consume across runs. It lets skills reuse prior work without treating reports as the source of truth.

For the full machine-readable contract, see [`chainlog-contract.md`](../reference/chainlog-contract.md).

## Purpose

Skills often collect data from multiple sources over multiple turns or sessions. A ticket-research skill gathers tracker data, relationships, and code evidence. A pull-request review skill gathers metadata, reviews, CI status, and static analysis. A planning skill gathers scope, constraints, and assumptions.

Without a shared primitive, each skill either regenerates everything on every run or invents its own ad-hoc state. Both patterns waste resources and produce inconsistent views. `chainlog` solves this by giving every skill a common, immutable, capability-typed observation ledger.

The key insight is that **reports are views, not timelines**. A report is a snapshot synthesized from the latest observations. Appending new sections to an old report would create contradictions. Instead, skills append new observations to a chain and regenerate the report from the latest observation per capability.

## When to use

A skill should use `chainlog` when it collects data from tools, APIs, MCP servers, or subagents that could be reused across runs, or when it synthesizes a report, review, debrief, plan, or other summary from collected data.

## When not to use

A skill should not use `chainlog` when it completes in one shot and never needs to share collected data, or when it only needs working state for itself. Use the [`stateful`](./stateful.md) pattern for private working state, and the [`context-reports`](./context-reports.md) pattern for final human-readable reports.

`chainlog` and `context-reports` can be used together: observations live in the chainlog, and the report is a view generated from them.

## Core concepts

| Term | Meaning |
|------|---------|
| **Work item** | The subject of investigation: a ticket, pull request, branch, commit, or other bounded unit. |
| **Capability** | The category of observation: `issue-tracker-source`, `pr-source`, `ci-source`, `static-analysis`, `changed-files`, `reviews`, `code-exploration`, etc. |
| **Observation** | A single immutable entry in the chain. It has frontmatter identifying the work item, capability, source, and timestamp, plus a payload body. |
| **Segment** | A bounded storage unit that holds a consecutive slice of observations for one work item. |
| **Chain** | The ordered sequence of segments for one work item, linked by reference to the previous segment. |
| **View** | A report, review, or summary generated from the latest observation per capability. |
| **Source** | The tool, adapter, or skill that produced the observation. |
| **Schema version** | The version of the observation envelope and the capability payload schema. |

## Design principles

1. **Append-only and immutable.** Observations are never deleted, modified, or compacted. Staleness is recorded by appending a marker, not by editing history.
2. **Work-item-scoped.** Every observation belongs to exactly one work item, identified by a stable key.
3. **Capability-typed.** Every observation has a capability. The latest observation per capability is the natural unit for building views.
4. **Sourced and timestamped.** Every observation records who produced it, when, and with what confidence.
5. **Storage-agnostic.** The default adapter writes linked markdown segments. Other adapters may write to graphs, vector stores, or harness memory, but they must expose the same operation contract and preserve the same ledger semantics.
6. **Views are generated, not stored.** Reports are derived from observations. A report may be persisted for human reading, but it is not an input to future reasoning unless it has been re-appended as a new observation.

## Position in the architecture

`chainlog` sits between the tool layer and the report layer. Tools and adapters produce observations; skills append them to the chainlog; consumers query the latest observations, check freshness, and synthesize views.

It is a peer to [`context-reports`](./context-reports.md), not a replacement. `context-reports` defines the shape of human-readable reports. `chainlog` defines the shape of machine-readable observations. A report is a view over observations; observations are not derived from reports.

`chainlog` also reinforces other architecture patterns:

- [`tooling-awareness`](../../fundamentals/architecture/tooling-awareness.md) — the storage adapter itself is a capability discovered through the same tooling-awareness rules.
- [`stateful`](./stateful.md) — state files hold working memory for one skill; the chainlog holds durable observations shared across skills.
- [`building-block`](./building-block.md) — a `chainlog` implementation is itself a narrow, reusable building block.
- [`conductor`](./conductor.md) — conductor skills are the most common producers and consumers of chainlog observations.

## Storage model

The default `chainlog` adapter stores observations as a chain of linked segments. Each segment holds a consecutive slice of observations for one work item. When a segment reaches its threshold, the adapter starts a new segment and links it to the previous one. Old segments are read-only; only the head segment accepts new observations.

This design avoids compaction, which would delete history and contradict the append-only property. It keeps files manageable while preserving the full chain for audit and replay.

For the full file layout, segment frontmatter, observation envelope, and storage adapter contract, see [`chainlog-contract.md`](../reference/chainlog-contract.md).

## Operations

A `chainlog` implementation exposes `append`, `query_latest`, `query_all`, `query_since`, `exists`, and `mark_stale`. The contract is fixed across adapters; only the invocation mechanism varies by harness.

See [`chainlog-contract.md`](../reference/chainlog-contract.md) for the full operation schemas, input/output shapes, and error contract.

## Producer and consumer responsibilities

### Producers

A skill that collects data from tools or subagents should append observations to `chainlog` before synthesizing a view. It must:

- Normalize the tool output to the relevant capability contract payload.
- Include all required envelope fields.
- Record the source, source version, and confidence honestly.
- Not store secret values in observations; only env-var names or references.
- Link to the view it generates, if any.

### Consumers

A skill that synthesizes output from prior observations should:

- Query `chainlog` for the latest observations per capability.
- Check whether each observation is still fresh before using it.
- Refresh stale observations by invoking the appropriate tool, not by editing the chain.
- Append new observations after collecting fresh data.
- Not trust observations produced by another skill without checking schema version and freshness.

## Freshness and staleness

`chainlog` does not judge freshness. It records `collected_at` and supports `mark_stale`, but the consumer must decide whether an observation is still usable. This mirrors the freshness rules in [`context-reports`](./context-reports.md): a view is only as fresh as the observations it was built from.

A consumer should consider an observation stale when:

- The underlying source has changed (e.g., a new commit was pushed, a ticket was updated, a new CI run completed).
- The schema version is incompatible with the consumer.
- A staleness marker exists for the capability.
- The observation predates a configured freshness window for time-sensitive capabilities.

When an observation is stale, the consumer should collect fresh data, append a new observation, and then synthesize its view.

## Identity and aliasing

If the same work item can be identified in multiple ways (e.g., a pull request number and a ticket key), the skill should normalize the key before appending or querying. `chainlog` itself does not resolve aliases; it stores and retrieves by the key it is given. Identity resolution is the responsibility of the skill or of a dedicated identity-resolution capability.

## Schema versioning

The envelope has a `schema_version` field. The payload schema is governed by the relevant capability contract. When a payload schema changes, the consumer must check `source_version` or `schema_version` before assuming the payload shape.

A chainlog implementation should not reject old observations. It should store them and let consumers decide whether they can still read them.

## Security

- Do not store secret values in observations.
- Scope observations to the project context directory; do not share them across projects unless the storage adapter is explicitly project-scoped.
- A skill should not trust observations produced by another skill without checking freshness and schema version.
- Append-only semantics prevent tampering with history, but they do not prevent poisoned observations. Consumers must evaluate source and confidence.

## Common mistakes

- **Treating reports as observations.** A report is a view. If you need its content in the chainlog, append the raw data that produced it, not the report itself.
- **Forgetting freshness checks.** Querying the chainlog without checking whether observations are stale produces stale views.
- **Storing secrets in observations.** Tokens, passwords, and private keys must never appear in the chainlog. Use references instead.
- **Inventing private storage formats.** If a skill stores collected data in its own file format, other skills cannot reuse it. Append to the chainlog instead.
- **Confusing state and observations.** State files are working memory for one skill. The chainlog is shared, durable evidence. Use each for its intended purpose.

## Relationship to other patterns

| Pattern | Role | How `chainlog` differs |
|---------|------|------------------------|
| [`context-reports`](./context-reports.md) | Shared human-readable reports. | `chainlog` holds machine-readable observations; reports are views over them. |
| [`stateful`](./stateful.md) | Working memory across invocations. | `chainlog` is shared across skills; state is private to one skill. |
| [`tooling-awareness`](../../fundamentals/architecture/tooling-awareness.md) | Capability-first tool selection. | `chainlog` uses tooling-awareness to discover its storage adapter. |
| [`building-block`](./building-block.md) | Narrow, reusable capabilities. | A `chainlog` implementation is a building block; the pattern defines how to use it. |

## Open decisions

The following details are intentionally left open until a concrete implementation is tested:

- **Segment threshold.** Should segmentation be based on file size, observation count, or time window?
- **Segment key format.** Should segments be named with a counter (`000`), a timestamp (`2026-07`), or a content hash?
- **Head pointer.** Should the current segment be tracked with a separate `.head` file, a `latest` naming convention, or a symlink?
- **Stale markers in queries.** Should `query_latest` exclude stale markers by default, or return them with a clear flag?
- **Cross-work-item queries.** Should the contract support queries that span related work items (e.g., a ticket and its pull request)?
- **Tamper evidence.** Should observations include content hashes to detect accidental or malicious modification?
- **Extended adapter queries.** Should storage adapters declare which extended queries they support beyond the base contract?

## Research basis

- The distinction between **immutable logs** and **derived views** is well established in event sourcing, CQRS, and change-data-capture systems.
- The need for skills to **share observations** without tight coupling is our own, supported by the broader research on composition, memory, and multi-session agents.
- The **append-only ledger** shape is our own, chosen to preserve provenance and make audits possible.
- The **segmented file layout** is our own, designed to keep files manageable without compaction.
- The **storage adapter contract** is our own, aligned with the tooling-awareness principle that capabilities should be backend-agnostic.
