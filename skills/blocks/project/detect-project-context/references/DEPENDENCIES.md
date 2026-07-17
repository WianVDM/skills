# Dependencies

## Required skills

None. `detect-project-context` is a standalone building block.

## `scripts/detect-project-context.py`

- **Python 3** — standard library only (`pathlib`, `argparse`, `json`).

## `scripts/resolve-standards-path.py`

- **Python 3** — standard library.
- **PyYAML** — used only for the config layer (`write-a-skill.yaml`). The import is lazy; without it the layer is skipped with a disclosure note.

## Required binaries

- `python3` (or equivalent Python 3 interpreter)

## Consumed references

- `{config_dir}/write-a-skill.yaml` — optional `standards_path` override, read by `resolve-standards-path.py`.
- `docs/skill-standards/` — located by walking up from the script for the bundle fallback.

## Environment variables

None.
