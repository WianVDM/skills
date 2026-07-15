# audit-skill chainlog declaration

This document declares that `audit-skill` does not participate in the [`chainlog`]({chainlog_pattern_path}) pattern as a producer or consumer of observations.

## Classification

`audit-skill` is **neither** a producer nor a consumer of chainlog observations.

Rationale: `audit-skill` evaluates whether other skills declare and use chainlog correctly. It reads skill files and checks for `references/chainlog.md`, but it does not append observations to a chainlog or synthesize views from observations.

## Why chainlog is not needed

- The skill only inspects skill files and reports findings.
- It does not collect data from tools for reuse across runs.
- It does not synthesize reports from tool-collected data.

## If this changes

If `audit-skill` later starts appending or querying chainlog observations directly, re-run `write-a-skill` to reclassify it and draft a producer, consumer, or both declaration.

## Related

- [`chainlog` pattern]({chainlog_pattern_path})
- [`chainlog-contract.md` reference]({chainlog_contract_path})
