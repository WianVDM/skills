# worker-contract

A vocabulary building block that provides the canonical worker/subagent return contract for conductors.

## When to use

Use this skill when:

- Composing a subagent prompt that needs the standard return contract.
- Standardizing how workers report status, findings, and blockers.
- Referencing the default forbidden actions, allowed tools, and scope boundaries for subagents.

## How to use

A conductor embeds this contract into a subagent prompt by:

1. Reading this skill's `SKILL.md` or invoking the `worker-contract` skill.
2. Prepending the standard contract to a worker-specific prompt.
3. Adding role, scope, and task-specific reasoning.

## Directory layout

```
worker-contract/
├── SKILL.md
├── README.md
├── references/
│   └── DEPENDENCIES.md
└── evals/
    └── evals.json
```

## Key conventions

- **Reference, not workflow:** this skill defines shared language, not a process.
- **Default contract:** the return format, forbidden actions, allowed tools, and scope boundaries are defaults.
- **Conductor customization:** conductors may add worker-specific overrides.
- **Read-only:** does not perform actions itself.

## Maintenance notes

- Keep the contract in sync with `docs/skill-standards/patterns/conductor.md`.
- Update the version when the return format changes.
- Add near-miss triggers to `evals/evals.json` if new domains collide with the worker concept.
