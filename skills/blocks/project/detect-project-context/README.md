# detect-project-context

A global, model-invoked building block that detects the project root and the canonical skills, context, and config directories, and resolves the skill-standards path.

## How to use

```bash
python scripts/detect-project-context.py --start . --json
python scripts/resolve-standards-path.py --start . --json
```

Use `--json` for structured output. The default is a short human summary.

## Caller rules

- Call `detect-project-context` before reading or writing any skill, context, or config files, and use the `recommended_*_dir` values as destinations.
- Confirm the detected `project_root` with the user when `confidence` is `low` or a `note` is present.
- `resolve-standards-path.py` discloses degraded mode; never silently fall back when it reports `status: missing`.

The contract, output schemas, marker table, and resolution order live in [SKILL.md](SKILL.md) and [references/INTERFACE.md](references/INTERFACE.md).

## When to maintain or extend this block

- A new marker convention needs to be recognized.
- The candidate or confidence rules change.
- The standards resolution order changes (keep `docs/skill-standards/fundamentals/architecture/standards-path.md` in sync).

## How to update

- Keep `SKILL.md` as the contract; schemas and algorithm detail belong in `references/INTERFACE.md`.
- Run the test suite (`python -m pytest scripts/tests/`) before publishing changes.
