# Dependencies

## Tools

- `bash` — executes the deterministic Python script.
- `read` — to inspect report frontmatter when the script is not used directly.

## Python standard library

- `argparse`, `json`, `sys`, `re`, `datetime`, `pathlib`

## Optional Python packages

- `pyyaml` — enables full YAML frontmatter parsing. If absent, the script falls back to a vendored regex-based parser for the fields it needs.

## Required skill dependencies

None. `scan-context` is a deterministic script that does not invoke other skills.

## Recommended skill dependencies

- `context-reports` — provides the canonical report directory layout, frontmatter schema, and freshness rules. The script reads reports directly, but follows the conventions defined by `context-reports` when present.

## Environment variables

None required.

## Binaries

None required beyond `python3`.
