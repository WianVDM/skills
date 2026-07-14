# list-available-skills

A model-invoked building block that discovers skills already available in the project and user scope.

## When to use

Use this skill when you need to know:

- What skills already exist in the current project.
- What skills are available in the user scope.
- The invocation mode and tags of existing skills.
- Whether an existing skill might cover a problem before creating a new one.

## How to use

Invoke the skill by name, or run the script directly:

```bash
python scripts/list-available-skills.py --project-root . --include-user --json
```

## Output

The skill returns a structured report with:

- `project_scope`: list of skill paths found in the project.
- `user_scope`: list of skill paths found in the user scope.
- `skills`: parsed records for each discovered skill.
- `errors`: list of skills whose frontmatter could not be parsed.

Each skill record includes `name`, `path`, `invocation`, `version`, and `tags`. `version` may be absent.

## Directory layout

```
list-available-skills/
├── SKILL.md
├── README.md
└── scripts/
    └── list-available-skills.py
```

## Key conventions

- **Read-only:** does not write or modify files.
- **Deterministic:** scans the same directories each time.
- **No user interaction:** the caller decides what to do with the results.
- **Harness-compatible:** scans native harness skill directories in addition to project-specific paths.

## Maintenance notes

- Frontmatter parsing is delegated to the shared `parse-skill-frontmatter` skill.
- Add new skill directory conventions by updating the candidate list in the script.
