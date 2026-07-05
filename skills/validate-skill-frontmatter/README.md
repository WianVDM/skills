# validate-skill-frontmatter

A model-invoked building block that validates `SKILL.md` YAML frontmatter against the canonical JSON schema.

## When to use

Use this skill when you need to:

- Confirm that a skill's frontmatter follows the standards.
- Integrate frontmatter validation into an audit or CI pipeline.
- Get line-level error reporting for frontmatter issues.

## How to use

Invoke the skill by name, or run the script directly:

```bash
python scripts/validate-skill-frontmatter.py skills/my-skill/SKILL.md
```

To use a custom schema:

```bash
python scripts/validate-skill-frontmatter.py skills/my-skill/SKILL.md --schema docs/custom/schema.json --json
```

## Output

The script returns a structured report:

- `valid`: `true` or `false`.
- `errors`: list of validation errors with `message`, `path`, and `line` (when available).

## Directory layout

```
validate-skill-frontmatter/
├── SKILL.md
├── README.md
└── scripts/
    └── validate-skill-frontmatter.py
```

## Key conventions

- **Schema-driven:** validates against the canonical schema from `docs/skill-standards/schemas/`.
- **Line-level reporting:** maps schema errors back to the original file when possible.
- **Read-only:** does not modify the target file.
- **Fail closed:** exits with a non-zero status if dependencies are missing.

## Maintenance notes

- Update the default schema path if the standards directory changes.
- Keep the error formatting stable so callers can parse the JSON output.
