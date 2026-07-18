---
name: eval-format
description: Provide the canonical schema and conventions for skill evaluation artifacts stored in evals/evals.json. Use when authoring, validating, or referencing trigger, behavior, composition, pressure, or security evals.
invocation: model-invoked

---

# eval-format

## Purpose

Provide the canonical schema, test types, baseline types, assertion types, and writing conventions for skill evaluation artifacts in `evals/evals.json`.

## Type

Vocabulary building block.

## In scope

- Define the `evals/evals.json` artifact schema.
- Document the supported test types and when to use each.
- Document baseline types for behavior tests.
- Document deterministic assertion types.
- Provide conventions for writing strong trigger evals.
- Reference the formal JSON Schema.

## Out of scope

- This skill does not run evals itself; runners and harnesses execute the tests.
- It does not generate evals automatically; generators like `run-trigger-evals` produce candidate cases that still require human review.
- It does not replace skill-specific evaluation strategy; each skill decides which test types it needs.

## When to use

- A skill author needs to write or validate `evals/evals.json`.
- A script needs to parse or validate evaluation artifacts.
- A skill wants to reference the canonical eval schema and conventions.

## Artifact schema

The canonical source of truth for the `evals/evals.json` schema is `docs/skill-standards/schemas/evals.json.schema.json`. This document provides a quick reference only; the JSON schema defines the authoritative field names, types, and constraints.

## Artifact schema (quick reference)

The evaluation artifact lives at `evals/evals.json` in the skill package.

Required top-level fields:

| Field | Type | Purpose |
|---|---|---|
| `version` | string | Schema version. Currently `"1"`. |
| `skill` | string | The skill under test. |
| `tests` | array | Test cases. |

For the full field specification, see the JSON schema.

## Test types

| Type | Purpose |
|------|---------|
| `trigger` | Does the description fire at the right times? |
| `behavior` | Does the skill improve the agent's output? |
| `composition` | Does the skill select, follow, and compose correctly with other skills? |
| `pressure` | Does a discipline skill resist rationalization? |
| `security` | Does the skill avoid unsafe behavior? |

## Trigger categories

Trigger tests use `category`:

- `should-trigger` — the prompt should load the skill.
- `should-not-trigger` — a near-miss prompt that shares keywords but should not load the skill.

## Baseline types

Behavior tests use `baseline_type`:

- `no_skill` — compare against the agent's default behavior.
- `previous_version` — compare against the prior version of the skill.
- `failure_documentation` — compare against the documented failure pattern.

## Assertion types

Deterministic assertions include:

- `file_read` — the agent read an expected file.
- `file_write` — the agent wrote an expected file.
- `command` — the agent ran an expected command.
- `output_contains` — the output contains expected text.
- `output_excludes` — the output excludes forbidden text.
- `output_format` — the output matches an expected format.
- `regex_match` — the output matches a regular expression.
- `regex_exclude` — the output does not match a regular expression.

## Writing strong trigger evals

- Include at least 10 `should-trigger` prompts that vary phrasing and do not name the skill explicitly.
- Include at least 10 `should-not-trigger` prompts that are near-misses: they share keywords but point to a different intent or domain.
- Keep prompts realistic and user-like.
- Avoid rigid template phrases that no human would use.

## Security

- Evals are static artifacts; they do not execute code or mutate state.
- Do not include secrets, tokens, or project-specific paths in prompts or expected values.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `docs/skill-standards/schemas/evals.json.schema.json`
- `docs/skill-standards/reference/evaluation-framework.md`
