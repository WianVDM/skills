# chainlog

Append-only storage for observations collected by tools.

## What it does

`chainlog` lets skills store and reuse per-capability observations. Instead of regenerating a whole report, a skill can store each tool's output as an observation and later query the latest entry per capability.

## Directory layout

```text
chainlog/
├── SKILL.md
├── README.md
├── config.yaml
├── scripts/
│   └── chainlog.py
├── references/
│   ├── INTERFACE.md
│   ├── STORAGE.md
│   └── DEPENDENCIES.md
└── evals/
    └── evals.json
```

## Key conventions

- Chains are append-only. Entries are never deleted or modified.
- Each entry belongs to one work item and one capability.
- The latest entry per capability is the current "source of truth" for that capability.
- Staleness is determined by consumers using `artifact-freshness`, not by `chainlog` itself.
- Work-item keys are slugged for safe filenames.

## When to maintain or extend this block

- The observation envelope needs new fields.
- New operations are needed.
- The storage layout needs to change (e.g., linked segments for large chains).

## Shared building blocks

- `worker-contract` — return format if invoked through a subagent.
- `context-reports` — conventions for context directory layout and report schemas.

## How to update

- Keep `SKILL.md` focused on intent and the envelope. Push storage details into `references/STORAGE.md`.
- Preserve backward compatibility for existing chains; new fields should be optional.
- Bump the skill version when the envelope or operations change.
