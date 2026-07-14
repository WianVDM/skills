# Dependencies

## Required skills

None. `validate-skill-frontmatter` is a standalone building block.

## Required tools and capabilities

- **Read filesystem** — reads the target `SKILL.md` and the JSON schema.
- **Python 3.x** — the script is written in Python.

## Required binaries

- `python3` (or equivalent Python 3 interpreter)

## Required MCP servers

None.

## Environment variables

None.

## Required Python packages

- **PyYAML** — parses the YAML frontmatter block.
- **jsonschema** — validates the parsed frontmatter against the JSON schema.

These packages are required; the script fails closed if either is missing.
