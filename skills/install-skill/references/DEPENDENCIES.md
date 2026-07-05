# Dependencies

## Required skills

- **detect-project-context** — resolves the recommended skills directory for project scope.

## Required tools and capabilities

- **Read filesystem** — reads the source path or downloads an archive URL.
- **Write filesystem** — copies skills into the target directory and records provenance.
- **Network access** — only when installing from an archive URL.
- **Run subprocesses** — used to invoke `detect-project-context`.
- **Python 3.x** — the script is written in Python.

## Required binaries

- `python3` (or equivalent Python 3 interpreter)

## Required MCP servers

None.

## Environment variables

None.

## Optional dependencies

None. The script uses only the Python standard library (`shutil`, `pathlib`, `json`, `datetime`, `argparse`, `subprocess`, `urllib`, `tarfile`, `zipfile`).
