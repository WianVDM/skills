---
name: run-trigger-evals
description: Generate and update trigger evals for model-invoked skills in evals/evals.json.
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [evals, testing, model-invoked, building-block]
  verification_level: declared
---

# run-trigger-evals

## Purpose

Produce `evals/evals.json` for a model-invoked skill so that the skill can be tested against should-trigger and should-not-trigger cases.

## Type

Building block.

## In scope

- Read the target skill's `SKILL.md` to extract description, triggers, and scope.
- Generate 10 should-trigger cases that clearly match the skill's routing surface.
- Generate 10 should-not-trigger cases that are close but outside the skill's scope.
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
2. **Read the skill description and triggers.**
   - **Completion criterion:** routing surface and scope boundaries are understood.
3. **Generate should-trigger cases.** Create 10 prompts that should cause the model to invoke the skill.
   - **Completion criterion:** cases cover the skill's distinct triggers and branches.
4. **Generate should-not-trigger cases.** Create 10 prompts that are adjacent but outside scope.
   - **Completion criterion:** cases test the boundaries without being adversarial.
5. **Write `evals/evals.json`.**
   - **Completion criterion:** the file exists and is schema-compliant.
6. **Return a summary report.**
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
- `docs/skill-standards/TRIGGER_EVALS.md`
