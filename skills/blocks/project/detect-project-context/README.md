# detect-project-context

A global, model-invoked building block that detects the project root and recommended directories for skills, context, and config.

## When to use

Use this skill when another skill or conductor needs to locate the project root or the canonical skills, context, and config directories without hardcoding paths.

## How to use

The skill can be invoked by name or by running its script directly:

```bash
python scripts/detect-project-context.py --start . --json
```

Use `--json` for structured output. The default is human-readable text.

A conductor should call `detect-project-context` before reading or writing any skill, context, or config files. Use the `recommended_*_dir` values as the destination for generated files, and confirm the detected `project_root` with the user if `confidence` is `low`.

## Output

The skill returns a report with:

- `project_root`: resolved project root, or `null` if none found.
- `marker`: detected marker directory (`.agents`, `.pi`, `agents`, ...) or `null`.
- `confidence`: `high`, `medium`, or `low`.
- `recommended_skills_dir`, `recommended_context_dir`, `recommended_config_dir`: preferred directories.
- `skills_dir_candidates`, `context_dir_candidates`, `config_dir_candidates`: full candidate lists.

See `SKILL.md` for the canonical behavior, output schema, and confidence rules.
