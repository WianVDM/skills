# Dependencies

## Required skills

- **parse-skill-frontmatter** — extracts canonical frontmatter fields from local registry entries.
- **install-skill** — consumed as the target of the `install_command` convenience field. The registry itself does not install skills, but it emits a valid command that `install-skill` must understand.

## Required tools and capabilities

- **Read filesystem** — for local registry searches.
- **Network access** — for remote registry searches (`skills_sh`, `github`, `url`, `npm`).
- **Run subprocesses** — for the `npm` source type handler.
- **Python 3.x** — the script is written in Python.

## Required binaries

- `python3` (or equivalent Python 3 interpreter)
- `npm` — only when using the `npm` source type handler.

## Required MCP servers

None.

## Environment variables

None.

## Optional dependencies

- **PyYAML** — used to parse `.agents/config/write-a-skill.yaml` if present. The script falls back to built-in defaults if PyYAML is not installed.
