# parse-skill-frontmatter

A model-invoked building block that extracts canonical frontmatter fields from a `SKILL.md` file.

## When to use

Use this skill when you need to read skill metadata such as `name`, `description`, `invocation`, and `tags` from a `SKILL.md` file. `version` is returned if present, but it is not required.

## How to use

Invoke the skill by name, or run the script directly:

```bash
python scripts/parse-skill-frontmatter.py skills/example-skill/SKILL.md --json
```

## Output

The skill returns a JSON object with:

- `name`: skill name.
- `description`: skill description.
- `version`: skill version, or `null` if absent.
- `invocation`: invocation mode.
- `tags`: list of tags from metadata.

## Directory layout

```
parse-skill-frontmatter/
├── SKILL.md
├── README.md
└── scripts/
    └── parse-skill-frontmatter.py
```

## Key conventions

- **Read-only:** does not write or modify files.
- **Deterministic:** returns the same fields for the same input.
- **No user interaction:** the caller decides what to do with the results.
- **Self-contained:** works with or without PyYAML installed.

## Maintenance notes

- Add new canonical fields by updating the `CANONICAL_FIELDS` tuple and parser.
- Keep the fallback parser minimal and aligned with the canonical frontmatter schema.
