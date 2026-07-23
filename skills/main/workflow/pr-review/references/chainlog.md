# pr-review chainlog declaration

This document declares how `pr-review` produces and consumes observations for the [`chainlog`](../../../../blocks/project/chainlog/SKILL.md) pattern.

Chainlog is **opt-in per run**: enabled for large PRs and resume runs, skippable for quick single-pass reviews. The decision is recorded in state.

## Classification

`pr-review` is a **producer and consumer** of chainlog observations.

Rationale: The skill reads prior observations about the pull request (source metadata, CI status, static analysis, reviews) to avoid re-invoking tools, refreshes stale observations when the source changes, appends new observations, and synthesizes a review view from the latest observations per capability.

## Work item types

This skill works with the following work item types:

- `pr`

## Produced capabilities

| Capability | Source tool/adapter | When appended | Capability contract |
| ---------- | ------------------- | ------------- | --------------------- |
| `pr-source` | resolved tool per `tool-discovery` | After fetching PR metadata | `pr-adapter-contract` |
| `ci-source` | resolved CI tool | After fetching CI status | `pr-adapter-contract` |
| `static-analysis` | resolved static-analysis tool | After fetching findings | resolved source shape |
| `reviews` | resolved tool per `tool-discovery` | After fetching existing reviews, threads, and conversation comments | `pr-adapter-contract` |
| `changed-files` | git / resolved tool | After fetching the diff | `pr-adapter-contract` |

## Consumed capabilities

| Capability | Purpose | Freshness rule | Query point |
| ---------- | ------- | -------------- | ----------- |
| `pr-source` | Avoid re-fetching PR metadata | New commit pushed, PR updated | On resume |
| `ci-source` | Avoid re-fetching CI status | New CI run completed | On resume |
| `static-analysis` | Avoid re-fetching findings | New analysis completed | On resume |
| `reviews` | Avoid re-fetching existing reviews | New review posted | On resume |
| `changed-files` | Avoid re-fetching diff | New commit pushed | On resume |

## Workflow integration

1. Query the chainlog for the latest observations per required capability using the work item identity.
2. Check each observation with `artifact-freshness`.
3. Refresh stale observations by invoking the selected tool.
4. Append new observations.
5. Synthesize the review view from the latest observations.

## Report linkage

The review draft and payload link back to the chainlog observations they were built from. Each observation includes a `related_report` field pointing to the generated review file under `{context_dir}/pr-review/{key}/`.

## Storage adapter

`pr-review` discovers available storage adapters via `tool-discovery` for the `chainlog-storage` capability. The file-based adapter is the default and the fallback. The selected adapter is recorded in the project state.

| Adapter | Status | Fallback |
| ------- | ------ | -------- |
| file-based (default) | default | none |
| richer adapter (if discovered) | detected / not detected | file-based |

## Secrets

No secret values are stored in chainlog observations. Only env-var names or references are used.

## Decisions

| Decision | Rationale |
| -------- | --------- |
| Classification: both. | The skill both reads prior observations and appends new ones. |
| Capabilities produced/consumed: PR, CI, static-analysis, reviews, changed-files. | These are the load-bearing data sources for a review. |
| Storage adapter: file-based default. | Simple, portable, and append-only. |

## Related

- [`chainlog` pattern](../../../../blocks/project/chainlog/SKILL.md)
- [`artifact-freshness` building block](../../../../blocks/project/artifact-freshness/SKILL.md)
- [`tool-discovery` building block](../../../../blocks/project/tool-discovery/SKILL.md)
