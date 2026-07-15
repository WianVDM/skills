# Dependencies

## Required

- **Python 3.10+** — scripts are written in Python 3.
- **PyYAML** — required for parsing and writing YAML frontmatter.

## Required skills

- `worker-contract` — return contract used if the block is invoked through a subagent.
- `context-reports` — conventions for context directory layout and report frontmatter.

## Recommended

- `artifact-freshness` — consumers use this block to determine whether observations are still usable.

## Optional

None.

## Binaries

None beyond Python and PyYAML.

## Consumed references

- `{context_dir}/chainlog/{work_item_type}/{work_item_key_slug}.chain.md` — read and appended by `chainlog.py`.

## Produced artifacts

- `{context_dir}/chainlog/{work_item_type}/{work_item_key_slug}.chain.md` — append-only observation chain for each work item.
