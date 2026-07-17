# initialize-skill

First-run config initializer for any skill.

## What it does

`initialize-skill` removes the boilerplate of detecting, merging, migrating, and persisting project-level configuration. A skill author declares defaults in a `config.yaml` and delegates first-run setup to this block. The public contract is in [SKILL.md](SKILL.md); script schemas are in [references/INTERFACE.md](references/INTERFACE.md).

## Directory layout

```text
initialize-skill/
├── SKILL.md                          # public contract
├── README.md                         # this file
├── scripts/
│   ├── initialize.py                 # propose and optionally write project config
│   ├── load-skill-config.py          # read-only config loader
│   └── tests/
│       └── test_initialize.py        # pytest suite for both scripts
├── references/
│   ├── INTERFACE.md                  # script input/output schemas
│   ├── CONFIG_FORMAT.md              # format expected from consuming skills
│   └── DEPENDENCIES.md               # classified dependency list
└── evals/
    └── evals.json                    # trigger, behavior, composition, and security evals
```

## When to maintain or extend this block

- The `config.yaml` format consumed by skills changes.
- The merge or migration rules need to change.
- A new config directory convention needs to be supported.

## How to update

- Keep `SKILL.md` focused on intent and contract. Push deep detail into `references/`.
- Preserve backward compatibility for existing project configs.
- Run the test suite (`python -m pytest scripts/tests/`) before publishing changes.
