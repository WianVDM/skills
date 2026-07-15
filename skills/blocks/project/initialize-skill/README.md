# initialize-skill

First-run config initializer for any skill.

## What it does

`initialize-skill` removes the boilerplate of detecting, merging, migrating, and persisting project-level configuration. It lets a skill author declare defaults in a `config.yaml` and delegates the first-run setup to this block.

## Directory layout

```text
initialize-skill/
├── SKILL.md                          # public contract
├── README.md                         # this file
├── config.yaml                       # this block's own config declaration
├── scripts/
│   ├── initialize.py                 # propose and optionally write project config
│   └── load-skill-config.py          # read-only config loader
├── references/
│   ├── INTERFACE.md                  # script input/output schemas
│   ├── CONFIG_FORMAT.md              # format expected from consuming skills
│   └── DEPENDENCIES.md               # classified dependency list
└── evals/
    └── evals.json                    # trigger and behavioral evals
```

## Key conventions

- The caller must obtain explicit user approval before invoking `initialize.py` with `--approve`.
- `load-skill-config.py` is read-only and safe to call at any time.
- Existing user edits are preserved during merge and migration.
- Only `{skill}.yaml` is written; `shared.yaml` is never modified by this block.
- Type mismatches are reported but do not prevent the config from being returned.

## When to maintain or extend this block

- The `config.yaml` format consumed by skills changes.
- The merge or migration rules need to change.
- A new config directory convention needs to be supported.

## Shared building blocks

- `detect-project-context` — provides the marker directory and config directory.
- `worker-contract` — return format used by subagents if the skill is invoked through them.
- `context-reports` — context report conventions if the block writes state.

## How to update

- Keep `SKILL.md` focused on intent and contract. Push deep detail into `references/`.
- Preserve backward compatibility for existing project configs.
- Bump the skill version when the interface or merge rules change.
