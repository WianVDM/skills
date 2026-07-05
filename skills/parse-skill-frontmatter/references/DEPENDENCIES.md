# Dependencies

## Required skills

None. `parse-skill-frontmatter` is a standalone building block.

## Required tools and capabilities

- **Read filesystem** — reads the target `SKILL.md` file.
- **Python 3.x** — the script is written in Python.

## Required binaries

- `python3` (or equivalent Python 3 interpreter)

## Required MCP servers

None.

## Environment variables

None.

## Optional dependencies

- **PyYAML** — used for full and correct YAML parsing when available. The script falls back to a minimal regex parser if PyYAML is not installed.
