# {skill-name} chainlog declaration

This document declares how `{skill-name}` consumes observations from the [`chainlog`]({chainlog_pattern_path}) pattern.

## Classification

`{skill-name}` is a **consumer** of chainlog observations.

Rationale: {why this skill reads observations without appending new ones}.

## Work item types

This skill consumes observations for the following work item types:

- {work_item_type, e.g., `ticket`, `pr`, `branch`, `commit`}

## Consumed capabilities

| Capability | Purpose | Freshness rule | Query point |
| ---------- | ------- | -------------- | ----------- |
| {capability-name} | {why the skill reads it} | {when it becomes stale} | {workflow step} |

## Workflow integration

Before invoking a tool, `{skill-name}` queries the chainlog for the latest observations per capability. Each observation is checked with `artifact-freshness` before use. Stale observations are refreshed by invoking the source tool, and the fresh result is appended to the chainlog by the refreshing step (if applicable).

Example `query_latest` invocation:

```json
{
  "operation": "query_latest",
  "context_dir": ".agents/context",
  "work_item_type": "{work_item_type}",
  "work_item_key": "{work_item_key}",
  "capability": "{capability-name}"
}
```

Workflow steps:

1. Query `chainlog/query_latest` for required capabilities using the invocation above.
2. Check each observation with `artifact-freshness`.
3. Refresh stale observations by invoking the appropriate tool.
4. Synthesize output from the latest observations.

## Report or view output

This skill does not produce a report or view. It uses chainlog observations to {describe the output, e.g., validate assumptions, make a pass/fail decision, etc.}.

## Storage adapter

`{skill-name}` reads from whichever storage adapter is active for the project. The file-based adapter is the default. If the skill reads from a richer adapter, it is recorded below.

| Adapter | Status | Fallback |
| ------- | ------ | -------- |
| file-based (default) | default | none |
| {richer adapter name} | {detected / not detected} | file-based |

## Secrets

No secret values are stored in chainlog observations. Only env-var names or references are used.

## Decisions

| Decision | Rationale |
| -------- | --------- |
| Classification: consumer. | {why} |
| Capabilities consumed: {list}. | {why} |
| Storage adapter: {choice}. | {why} |

## Related

- [`chainlog` pattern]({chainlog_pattern_path})
- [`chainlog-contract.md` reference]({chainlog_contract_path})
- [`artifact-freshness` building block]({artifact_freshness_path})
- [`tool-discovery` building block]({tool_discovery_path})
