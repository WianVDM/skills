# The objective map

Every `write-a-skill` branch starts at phase 0: building the objective map with the user and getting it confirmed. Nothing downstream — gates, patterns, files — runs on an unconfirmed map.

## The nine fields

| Field | Question it answers |
|---|---|
| Core objective | What single judgment or process does this skill make predictable? (the litmus statement) |
| Consumers | Who reaches for it — the user, the agent, other skills? |
| Triggers | What prompts or situations should fire it? Feeds the description design phase. |
| Coverage | What must it handle? (in-scope) |
| Non-goals | What must it refuse to do? (out of scope) |
| Capabilities | What must it be able to *do*? Drives capability-to-tool design. |
| Success criteria | What does "working" look like? Feeds evals. |
| Constraints | Harness, project, security, portability requirements. |
| Shape hypothesis | First guess at type, confirmed later against the types taxonomy. |

## The protocol

1. **Prefill-and-confirm first.** The conductor (or the `map-objective` worker) drafts the full map from the user's request and presents it whole. Questions are for gaps and corrections, not a field-by-field interrogation.
2. **Grill the gaps.** For missing or shaky fields, ask one question at a time. Every question ships with options and a recommended default, plus the reason for the recommendation.
3. **Iterate until sign-off.** Revise the map and re-present it after every answer. The map is confirmed only when the user explicitly says so.
4. **Persist.** The confirmed map is written to the intent note (`{context}/skill-design/{skill-name}-intent.md`). It is append-refined, never silently overwritten.
5. **Return on contradiction.** If a later phase discovers something that contradicts the map, the conductor returns to the map instead of patching locally.

## Change-branch variant

For the `change` branch, the map is rebuilt from the target skill's files (`SKILL.md`, README, references) instead of from a user request. The rebuilt map — what the skill is for, who consumes it, what it covers — is presented to the user as the comprehension brief. **Scoring never starts on an unconfirmed brief.**

## Multi-skill boundary

When the idea implies two or more skills (a conductor plus its building blocks), map the set: one objective map per skill plus a shared composition sketch. Do not force multiple skills into one map.
