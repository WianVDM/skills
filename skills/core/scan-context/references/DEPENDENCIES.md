# Dependencies

## Tools

- `python3` — required for `scripts/scan-context.py`.
- `read` — to inspect report frontmatter when the script is not used directly.
- `find` / `bash` — optional; the script uses Python's standard library instead.

## Python standard library

- `argparse`, `json`, `sys`, `re`, `datetime`, `pathlib`

## Optional Python packages

- `pyyaml` — enables full YAML frontmatter parsing. If absent, the script falls back to a regex-based parser for the fields it needs.

## Required skills

- `context-reports` — provides the canonical report directory layout, frontmatter schema, and freshness rules.
- `worker-contract` — provides the canonical return contract for subagents and workers.

## Environment variables

None required.

## Binaries

None required beyond `python3`.
