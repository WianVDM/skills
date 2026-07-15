# identity-resolver

Resolve a work item from user input.

## What it does

`identity-resolver` turns a vague reference into a normalized identity envelope. It supports ticket keys, PR numbers, PR URLs, branch names, and commit hashes. Downstream skills can use the result without re-implementing parsing and git detection.

## Directory layout

```text
identity-resolver/
├── SKILL.md
├── README.md
├── config.yaml
├── scripts/
│   └── resolve-identity.py
├── references/
│   ├── INTERFACE.md
│   └── DEPENDENCIES.md
└── evals/
    └── evals.json
```

## Key conventions

- Work-item types are `ticket`, `pr`, `branch`, `commit`.
- The returned `key` is stable for the work item type.
- PR keys are formatted as `{number}@{owner-repo}`.
- Ticket keys are the matched ticket identifier.
- Branch and commit keys are the normalized branch or commit hash.
- The block is read-only; it never writes files.

## When to maintain or extend this block

- Add a new work-item type.
- Change the normalization rules.
- Add support for a new git provider URL format.

## Shared building blocks

- `detect-project-context` — discover project root, config dir, and context dir.
- `tool-discovery` — find the best `pr-source` adapter when a PR needs to be resolved.
- `worker-contract` — return format if invoked through a subagent.
- `context-reports` — conventions for context directory layout.

## How to update

- Keep parsing rules deterministic and testable.
- Preserve backward compatibility for existing key formats.
- Bump the skill version when the envelope or normalization changes.
