# eval-format

A vocabulary building block that provides the canonical schema and conventions for skill evaluation artifacts.

## When to use

Use this skill when:

- Writing or validating `evals/evals.json` for a skill.
- Referencing the canonical test types, baseline types, or assertion types.
- Building a tool that parses or validates evaluation artifacts.

## How to use

A skill references this contract by:

1. Reading this skill's `SKILL.md` or invoking the `eval-format` skill.
2. Applying the `evals/evals.json` schema and conventions.
3. Writing skill-specific test cases that follow the schema.

## Directory layout

```
eval-format/
├── SKILL.md
├── README.md
├── references/
│   └── DEPENDENCIES.md
└── evals/
    └── evals.json
```

## Key conventions

- **Reference, not runner:** this skill defines the artifact format, not the execution engine.
- **Schema-driven:** the canonical schema is in `docs/skill-standards/schemas/evals.json.schema.json`.
- **Deterministic assertions first:** prefer file, command, and string checks over LLM-as-judge.
- **Trigger evals are critical for model-invoked skills:** aim for 10 should-trigger and 10 should-not-trigger near-miss cases.

## Maintenance notes

- Update this skill when the `evals/evals.json` schema changes.
- Keep the assertion and test-type lists in sync with the formal schema.
- Add near-miss triggers to `evals/evals.json` if new evaluation domains could collide with this skill.
