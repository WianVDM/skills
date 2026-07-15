# {skill-name} chainlog declaration

This document declares that `{skill-name}` does not participate in the [`chainlog`]({chainlog_pattern_path}) pattern.

## Classification

`{skill-name}` is **neither** a producer nor a consumer of chainlog observations.

Rationale: {why this skill does not collect or consume observable data}.

## Why chainlog is not needed

- {reason, e.g., the skill only emits guidance based on user input}
- {reason, e.g., the skill maintains only private state}
- {reason, e.g., the skill completes in one shot and has no data to share}

## If this changes

If `{skill-name}` later collects data from tools or synthesizes a view from such data, re-run `write-a-skill` to reclassify it and draft a producer, consumer, or both declaration.

## Related

- [`chainlog` pattern]({chainlog_pattern_path})
- [`chainlog-contract.md` reference]({chainlog_contract_path})
