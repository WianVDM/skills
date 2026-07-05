# run-trigger-evals

A model-invoked building block that generates trigger evals for model-invoked skills.

## When to use

Use this skill when you need to:

- Create `evals/evals.json` for a newly drafted model-invoked skill.
- Update trigger evals after a skill's description or triggers change.
- Validate an existing evals file against the schema.

## How to use

Invoke the skill by name, or run the script directly:

```bash
# Generate starter evals for a skill
python scripts/run-trigger-evals.py skills/my-skill

# Validate an existing evals file
python scripts/run-trigger-evals.py skills/my-skill --validate --json

# Seed or replace generated evals with an existing file
python scripts/run-trigger-evals.py skills/my-skill --input new-evals.json
```

## Output

The script creates or updates `skills/my-skill/evals/evals.json` and returns a summary:

- `skill`: the target skill name.
- `path`: path to the generated evals file.
- `valid`: whether the file passes schema validation.
- `should_trigger_count`: number of should-trigger cases.
- `should_not_trigger_count`: number of should-not-trigger cases.

## Directory layout

```
run-trigger-evals/
├── SKILL.md
├── README.md
├── references/
│   └── EVAL_FORMAT.md
└── scripts/
    └── run-trigger-evals.py
```

## Key conventions

- **Model-invoked only:** the building block is for skills that route autonomously.
- **Schema-compliant:** validates against the canonical evals schema.
- **Starter quality:** the script generates baseline cases; the model should refine them to match the skill's routing surface.
- **No execution:** does not run the evals against the skill.

## Maintenance notes

- Frontmatter parsing is delegated to the shared `parse-skill-frontmatter` skill.
- Improve the case-generation logic as the standards for trigger evals evolve.
- Keep the eval schema path in sync with `docs/skill-standards/schemas/evals.json.schema.json`.
- Keep the eval format reference in sync with `docs/skill-standards/TRIGGER_EVALS.md`.
