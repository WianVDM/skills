---
name: index-skill-capabilities
description: Generate a structured, deterministic capability index from skill files so other skills can discover, rank, and compare capabilities across the skill catalog.
invocation: model-invoked
type: building-block
depends:
  - parse-skill-frontmatter
  - context-reports
---

# index-skill-capabilities

## Purpose

Produce a machine-readable capability index from the skill files in this bundle. The index describes what each skill does, which capabilities it implements, and how those capabilities relate to other skills. Other skills and conductors can use the index to find overlaps, rank alternatives, and identify extraction opportunities without re-reading every `SKILL.md`.

## Type

Building block. The skill is deterministic and read-only. It does not make design decisions or modify skills.

## In scope

- Read `skills.json` to discover the skill bundle.
- Parse each skill's `SKILL.md` frontmatter and sections.
- Discover each skill's `subagents/`, `scripts/`, `references/`, and `config.yaml`.
- Map extracted capabilities to a controlled taxonomy.
- Emit a versioned JSON index.
- By default, write the index to the configured output path, falling back to `.agents/skill-capability-index.json` in the detected project (project-local override). Bundle CI can override this with `--output <path>` to commit the index elsewhere, such as `docs/skill-capability-index.json`.
- Validate an existing index against current source files without overwriting it.
- Record freshness metadata so consumers can detect stale indices.

## Out of scope

- This skill does not decide whether a capability should be extracted; it only produces the data that lets other skills make that decision.
- It does not index user-scope or third-party registry skills in v1, though the schema supports them.
- It does not use LLM-based semantic similarity; matching is deterministic.
- It does not modify skill files or the bundle manifest.

## When to use

- A conductor needs to know what capabilities already exist in the catalog.
- `detect-skill-overlap` or `write-a-skill` needs to compare a target skill against the catalog.
- A CI pipeline needs to regenerate the index after skill changes.
- A user wants to know which skill implements a specific capability.

## Inputs

```yaml
---
output: .agents/skill-capability-index.json   # optional; use docs/... for bundle CI
schema_version: 1.0.0                         # optional
---
```

## Outputs

A JSON file matching the schema in `references/INDEX_SCHEMA.md`.

## Workflow

1. **Load bundle manifest.** Read `skills.json` from the detected repo root.
2. **Index each skill.** For each skill path, parse `SKILL.md`, discover files, and extract capabilities.
3. **Map capabilities.** Map each capability to a taxonomy category using deterministic keyword rules.
4. **Emit index.** Write the JSON index with schema version, timestamp, and freshness metadata.
5. **Validate (optional).** If `--check` is passed, validate an existing index and report staleness or schema mismatches.

## Completion criteria

- The index is valid JSON and matches the schema in `references/INDEX_SCHEMA.md`.
- Every skill in `skills.json` has an entry.
- The `--check` mode returns success for a freshly generated index.
- `audit-skill` passes without blockers.

## Dependencies

- `parse-skill-frontmatter` — recommended; the generator can parse frontmatter itself, but the canonical parser is preferred when available.
- `context-reports` — recommended; the generator follows shared context-report conventions for output paths and freshness.
- `pyyaml` — used for YAML frontmatter and config parsing.

## References

- [Index schema](references/INDEX_SCHEMA.md) — canonical schema for the generated JSON.
- [Dependencies](references/DEPENDENCIES.md) — full dependency surface.
- `scripts/index-skill-capabilities.py` — the generator script.
- `scripts/tests/test_index_skill_capabilities.py` — unit tests.

## Security

- The skill is read-only; it does not write to skill files.
- It does not read secrets or tokens.
- It resolves paths from the detected repo root, not from user input.

## Evaluation

- Trigger evals: see `evals/evals.json`.
- Composition tests: verify that the index contains expected capabilities for representative skills.
- Pressure tests: missing skills.json, malformed frontmatter, empty skill directories.
