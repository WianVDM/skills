# write-a-skill chainlog declaration

This document declares that `write-a-skill` does not participate in the [`chainlog`]({chainlog_pattern_path}) pattern as a producer or consumer of observations.

## Classification

`write-a-skill` is **neither** a producer nor a consumer of chainlog observations.

Rationale: `write-a-skill` is a meta-level conductor. It classifies other skills and drafts `references/chainlog.md` declarations for them, but it does not append observations to a chainlog or synthesize views from observations for its own work.

## Why chainlog is not needed

- The skill only emits guidance and skill files based on user input and standards docs.
- It does not collect data from tools for reuse across runs.
- It does not synthesize reports from tool-collected data.

## If this changes

If `write-a-skill` later starts appending or querying chainlog observations directly (for example, to resume from prior design sessions), re-run `write-a-skill` to reclassify it and draft a producer, consumer, or both declaration.

## Related

- [`chainlog` pattern]({chainlog_pattern_path})
- [`chainlog-contract.md` reference]({chainlog_contract_path})
