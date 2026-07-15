# artifact-freshness chainlog declaration

This document declares that `artifact-freshness` does not participate in the [`chainlog`]({chainlog_pattern_path}) pattern as a producer or consumer of observations.

## Classification

`artifact-freshness` is **neither** a producer nor a consumer of chainlog observations.

Rationale: `artifact-freshness` judges whether an observation or report is fresh enough to reuse. It reads chainlog observations provided by callers, but it does not append to a chainlog or synthesize views from observations.

## Why chainlog is not needed

- The skill only evaluates freshness of supplied artifacts.
- It does not collect data from tools for reuse across runs.
- It does not synthesize reports from tool-collected data.

## If this changes

If `artifact-freshness` later starts appending to or querying a chainlog directly, re-run `write-a-skill` to reclassify it and draft a producer, consumer, or both declaration.

## Related

- [`chainlog` pattern]({chainlog_pattern_path})
- [`chainlog-contract.md` reference]({chainlog_contract_path})
- [`artifact-freshness` interface](INTERFACE.md)
