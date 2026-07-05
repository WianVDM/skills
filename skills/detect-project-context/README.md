# detect-project-context

A global, model-invoked building block that detects the project root and recommended directories for skills, context, and config.

## When to use

Use this skill when another skill or conductor needs to:

- Locate the project root.
- Find the canonical skills directory.
- Find the canonical context directory.
- Find the canonical config directory.
- Avoid hardcoding project-specific paths.

## How to use

The skill can be invoked by name or by running its script directly:

```bash
python scripts/detect-project-context.py --start . --json
```

By default, the script prints human-readable output. Use `--json` for structured output.

## Output

The skill returns a report with:

- `project_root`: resolved project root.
- `marker`: detected marker directory (`.agents`, `.pi`, `agents`) or `null`.
- `confidence`: `high`, `medium`, or `low`.
- `recommended_skills_dir`: preferred skills directory.
- `recommended_context_dir`: preferred context directory.
- `recommended_config_dir`: preferred config directory.
- `skills_dir_candidates`, `context_dir_candidates`, `config_dir_candidates`: full candidate lists.

## Directory layout

```
detect-project-context/
├── SKILL.md
├── README.md
└── scripts/
    └── detect-project-context.py
```

## Key conventions

- **Read-only:** the script never writes files or creates directories.
- **Deterministic:** the same starting directory always produces the same output.
- **No user interaction:** the skill reports detection results; the caller decides whether to ask for confirmation.
- **Harness-agnostic:** detection rules are based on directory layout, not harness-specific APIs.

## Maintenance notes

- Add new marker directories by updating the `MARKER_DIRS` list in the script.
- Add new candidate directory patterns by updating the detection logic.
- Keep the script compatible with Python 3 standard library only.
