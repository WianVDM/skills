# Dependencies

## Required

- **Python 3.10+** — scripts are written in Python 3.
- **PyYAML** — required for parsing and writing YAML frontmatter.

## Required skills

- `worker-contract` — return contract used if the block is invoked through a subagent.
- `context-reports` — conventions for context directory layout and report frontmatter.

## Recommended

- `artifact-freshness` — consumers use this block to determine whether evidence is still usable.

## Optional

None.

## Binaries

None beyond Python and PyYAML.

## Consumed references

- `{context_dir}/evidence/{work_item_type}/{work_item_key_slug}.timeline.md` — read and appended by `evidence-store.py`.

## Produced artifacts

- `{context_dir}/evidence/{work_item_type}/{work_item_key_slug}.timeline.md` — append-only evidence timeline for each work item.
