# JSON Schemas

This directory contains JSON Schema files for the portable skill standards. They are intended for tooling, validation, and reference. Each schema is a draft 2020-12 schema.

| File | Describes |
|------|-----------|
| `skill-frontmatter.schema.json` | YAML frontmatter for `SKILL.md`. |
| `skills.json.schema.json` | Package manifest `skills.json`. |
| `evals.json.schema.json` | Evaluation artifact `evals/evals.json`. |
| `skills.lock.schema.json` | Generated lock file `skills.lock`. |

The canonical specifications live in the markdown documents:

- `FORMAT.md` — the `SKILL.md` frontmatter and portable core.
- `PACKAGE.md` — the package envelope, lifecycle, and schemas.
- `EVALUATION.md` — the evaluation framework and assertion semantics.

Schemas are forward-compatible: they allow additional properties where the standard says harnesses should ignore unknown fields, and they constrain the fields required for portable interchange.
