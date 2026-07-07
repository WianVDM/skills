# Dependencies

## Required skills

- **parse-skill-frontmatter** — extracts the skill name and description from the target `SKILL.md`.

## Required tools and capabilities

- **Read filesystem** — reads the target skill's `SKILL.md` and the evals schema.
- **Write filesystem** — creates or updates `evals/evals.json` in the target skill directory.
- **Python 3.x** — the script is written in Python.

## Required binaries

- `python3` (or equivalent Python 3 interpreter)

## Required MCP servers

None.

## Environment variables

None.

## Optional dependencies

- **jsonschema** — used to validate the generated `evals/evals.json` against the schema. Validation is skipped if `jsonschema` is not installed.
