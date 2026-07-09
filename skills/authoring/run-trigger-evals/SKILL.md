---
name: run-trigger-evals
description: Generate and update trigger evals for model-invoked skills in evals/evals.json.
version: 1.0.1
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [authoring, building-block, evals, testing]
depends:
  - parse-skill-frontmatter
---

# run-trigger-evals

## Purpose

Produce `evals/evals.json` for a model-invoked skill so that the skill can be tested against should-trigger and should-not-trigger cases.

## Type

Building block.

## In scope

- Read the target skill's `SKILL.md` to extract the description, `When to use` list, and branch entry table.
- Generate branch-aware `should-trigger` cases from distinct triggers and use cases.
- Generate plausible near-miss `should-not-trigger` cases from the skill description and branches.
- Merge newly generated cases with existing `evals/evals.json` when `--input` is provided, replacing cases by ID while preserving unmatched existing cases.
- Write or update `evals/evals.json` in the target skill directory.
- Validate the output against the evals schema.

## Out of scope

- Running behavioral or composition tests.
- Evaluating the skill's performance.
- Generating evals for user-invoked skills (they have no model trigger).

## When to use

A model-invoked skill has been drafted and needs trigger evals before validation or sharing.

## Steps

1. **Accept the target skill path.**
   - **Completion criterion:** the target skill directory is identified.
2. **Read the skill description, `When to use` list, and branch table.**
   - **Completion criterion:** routing surface, branches, and scope boundaries are understood.
3. **Generate `should-trigger` cases.** Create distinct prompts from each branch trigger and each `When to use` item.
   - **Completion criterion:** each case maps to a distinct branch or intent, not a synonym.
4. **Generate `should-not-trigger` cases.** Create plausible near-miss prompts that are adjacent to the skill but outside its scope.
   - **Completion criterion:** cases are near-misses, not just negations of the action phrase.
5. **Merge with existing evals when `--input` is provided.**
   - Replace cases that share an ID with the newly generated ones; keep the rest.
   - **Completion criterion:** the merged set includes both preserved and updated cases without duplicates.
6. **Write `evals/evals.json`.**
   - **Completion criterion:** the file exists and is schema-compliant.
7. **Return a summary report.**
   - **Completion criterion:** counts and file path are reported.

## Eval format

See [`references/EVAL_FORMAT.md`](references/EVAL_FORMAT.md) for the `evals/evals.json` schema, field definitions, and validation details.

## Quality rules

- **Distinct triggers:** each should-trigger case maps to a different intent or branch, not synonyms.
- **Boundary testing:** should-not-trigger cases should be close enough to be plausible false positives.
- **No leakage:** cases should not include the exact skill name unless the skill is explicitly invoked by name.
- **Harness-agnostic:** prompts are written from the user's perspective, not a specific harness.

## Security

- Only writes files inside the target skill directory.
- Does not execute the skill during eval generation.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `docs/skill-standards/schemas/evals.json.schema.json`
- `docs/skill-standards/reference/trigger-evals.md`
- [`references/VALIDATION_TEST.md`](references/VALIDATION_TEST.md) — how to verify generated evals pass schema validation.
