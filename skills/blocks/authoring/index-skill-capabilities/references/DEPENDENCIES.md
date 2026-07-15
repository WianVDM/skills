# Dependencies

## Required

- `pyyaml` — parsing YAML frontmatter and `config.yaml` files.
- `skills.json` — the bundle manifest that lists all skills.

## Recommended

- `parse-skill-frontmatter` — canonical frontmatter parser. The generator includes a fallback parser, but prefers the canonical one when available.
- `context-reports` — shared conventions for output paths and freshness metadata.

## Optional

None.

## Runtime binaries

- Python 3.x

## Consumed references

- `references/INDEX_SCHEMA.md` — defines the output schema.
- Each skill's `SKILL.md`, `README.md`, `references/`, `subagents/`, `scripts/`, and `config.yaml`.

## Produced artifacts

- `docs/skill-capability-index.json` — the generated index.
