# artifact-freshness

Check whether a context report or evidence-store entry is fresh enough to reuse.

## What it does

`artifact-freshness` centralizes the decision of whether an artifact is stale. It reads report frontmatter or accepts evidence entries directly, checks multiple dimensions, and returns a structured result with a reason.

## Directory layout

```text
artifact-freshness/
├── SKILL.md
├── README.md
├── config.yaml
├── scripts/
│   └── check-freshness.py
├── references/
│   ├── INTERFACE.md
│   └── DEPENDENCIES.md
└── evals/
    └── evals.json
```

## Key conventions

- The block is read-only; it never fetches new data or writes files.
- Missing freshness metadata is treated as stale, not fresh.
- Git auto-detection is used only when the caller does not provide branch/commit.
- The result includes per-dimension details so the caller can decide which dimensions matter.

## When to maintain or extend this block

- New freshness dimensions are needed.
- The report frontmatter format evolves.
- The evidence-store entry format changes.

## Shared building blocks

- `worker-contract` — return format if invoked through a subagent.
- `context-reports` — conventions for report frontmatter and freshness vocabulary.

## How to update

- Keep `SKILL.md` focused on intent and dimensions. Push deep detail into `references/INTERFACE.md`.
- Preserve backward compatibility for existing consumers.
- Bump the skill version when the interface or dimension rules change.
