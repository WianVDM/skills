# Dependencies

## Required skills

- **validate-skill-frontmatter** — invoked by the audit script for frontmatter schema validation.

## Recommended skills

- **detect-skill-overlap** — used in the overlap-detection step to compare the target skill with the existing catalog.

## Required tools and capabilities

- **Read filesystem** — reads `SKILL.md`, `README.md`, references, subagents, and scripts from the skill under audit.
- **Run scripts** — executes the bundled Python audit script.
- **Python 3.x** — the script is written in Python.

## Required binaries

- `python3` (or equivalent Python 3 interpreter)

## Required MCP servers

None.

## Environment variables

None.

## Optional Python packages

- **PyYAML** — used by `validate-skill-frontmatter` and by the audit script's fallback YAML parser when available. The script works without it, but full frontmatter parsing is degraded.

## Consumed references

- `docs/skill-standards/reference/audit-rubric.md` — canonical audit rubric.
- `docs/skill-standards/schemas/skill-frontmatter.schema.json` — canonical frontmatter schema.
- A bundled copy of the schema may be used as a fallback when the canonical docs are not available.
