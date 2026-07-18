# pr-report chainlog declaration

This document declares how `pr-report` produces and consumes observations for the [`chainlog`](../../../../blocks/project/chainlog/SKILL.md) pattern.

## Classification

`pr-report` is a **producer and consumer** of chainlog observations.

Rationale: the Collect phase gathers load-bearing tool results per capability, and every report after the first is a delta against the previous iteration. Storing each tool result as an observation lets later runs reuse fresh data, compute "what changed since the last look" over observations instead of re-fetching, and keeps the report traceable to its sources.

## Work item types

- `pr` — keyed by the ticket key when one exists, otherwise `pr-{number}`.

## Produced capabilities

Every load-bearing tool result is appended after normalization, during Phase 4 (Collect):

| Capability | Source tool/adapter | When appended | Capability contract |
| ---------- | ------------------- | ------------- | ------------------- |
| `pr-source` | discovered PR tool or `github-pr-adapter` | After PR metadata is collected | `pr-adapter-contract` |
| `changed-files` | discovered PR tool or git | After the diff is collected | `pr-adapter-contract` |
| `reviews` | discovered PR tool | After top-level reviews are collected | `pr-adapter-contract` |
| `threads` | discovered PR tool | After inline threads are collected | `pr-adapter-contract` |
| `conversation-comments` | discovered PR tool (`/issues/{n}/comments`) | After conversation comments are collected | `pr-adapter-contract` notification/comment shape |
| `ci-source` | discovered CI tool or `github-actions-adapter` | After check runs are collected | `pr-adapter-contract` |
| `static-analysis` | discovered analysis tool or `sonarcloud-adapter` | After findings are collected | `pr-adapter-contract` |
| `issue-tracker-scope` | discovered tracker tool or `jira-adapter` | After scope is collected | `pr-adapter-contract` |

## Consumed capabilities

Queried in Phase 2a, before collection:

| Capability | Purpose | Freshness rule | Query point |
| ---------- | ------- | -------------- | ----------- |
| All produced capabilities | Reuse fresh observations; baseline for delta computation | Stale when the PR head commit changes, a new CI run or analysis completes, or a new review/comment is posted | Phase 2a |

Each observation returned by `query_latest` is checked with `artifact-freshness`. Stale observations are refreshed by re-invoking the capability's best available tool in Phase 4.

## Inconclusive observations

An observation whose tool result was silently empty or unverifiable (e.g., wrong-cased project key, nonexistent analysis, 404 from the preferred tool) is appended with `inconclusive: true` and `confidence: low`. Delta computation and triage must never treat an inconclusive observation as negative evidence; it is refreshed or escalated on the next run instead.

## Workflow integration

1. Phase 2a: query `chainlog/query_latest` per capability for the work item.
2. Check each observation with `artifact-freshness`.
3. Phase 4: refresh stale observations via the best available tool; normalize via `normalize-observation`.
4. Append every collected result with `chainlog/append`, including inconclusive markers.
5. Synthesize the report from the latest observations.

## Report linkage

The report links back to the observations it was built from. Each observation appended during a run records `related_report` pointing to `{context_dir}/pr-report/{key}-report.md`.

## Storage adapter

`pr-report` discovers available storage adapters via `tool-discovery` for the `chainlog-storage` capability. The file-based adapter is the default and the fallback.

| Adapter | Status | Fallback |
| ------- | ------ | -------- |
| file-based (default) | default | none |
| richer adapter (if discovered) | detected / not detected | file-based |

## Secrets

No secret values are stored in chainlog observations. Only env-var names or references are used.

## Decisions

| Decision | Rationale |
| -------- | --------- |
| Classification: both. | The skill collects tool results (producer) and every run after the first is a delta over prior observations (consumer). |
| Inconclusive marker. | Field report: silently-empty results (wrong-cased keys, missing analyses) must never be stored as truth and reused in deltas. |
| Storage adapter: file-based default. | Simple, portable, append-only. |

## Related

- [`chainlog` building block](../../../../blocks/project/chainlog/SKILL.md)
- [`chainlog-contract.md` reference](../../../../../docs/skill-standards/reference/chainlog-contract.md)
- [`artifact-freshness` building block](../../../../blocks/project/artifact-freshness/SKILL.md)
- [`tool-discovery` building block](../../../../blocks/project/tool-discovery/SKILL.md)
