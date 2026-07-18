# Chainlog design checklist

This checklist applies when a skill being designed collects or consumes observable data (chainlog classification is not `neither`). The conductor confirms each applicable item with the user before the Draft phase; items that do not apply are recorded with rationale in the decision log.

- **Chainlog classification.** The skill is classified as producer, consumer, both, or neither. A `neither` classification needs no file; anything else is recorded in `references/CHAINLOG.md`.
- **Chainlog producer check.** If producer or both, the skill appends every load-bearing tool result to `chainlog` before synthesizing a view.
- **Chainlog consumer check.** If consumer or both, the skill queries `chainlog` for reusable observations before invoking tools.
- **Chainlog freshness.** If consumer or both, the skill uses `artifact-freshness` to judge whether observations are still usable.
- **Chainlog schema.** If producer or both, the skill documents which capability contract defines the payload schema for each observation.
- **Chainlog identity.** If producer or both, the skill normalizes the `work_item_key` before appending or querying.
- **Chainlog storage adapter.** If producer or both, the default file adapter is confirmed and any richer adapter is discovered via `tool-discovery`.
- **Chainlog report linkage.** If the skill generates a view, it links the view back to the observations it was built from.
- **Chainlog secrets.** No secret values are stored in chainlog observations.
