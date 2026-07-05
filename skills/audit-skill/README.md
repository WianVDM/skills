# audit-skill

A model-invoked building block that checks a skill against the skill fundamentals and produces a structured audit report.

## When to use

Use this skill when you need to:

- Validate a skill before publishing or sharing it.
- Check a draft skill before writing files.
- Run a standards-compliance check in CI.
- Produce a remediation plan for a skill that drifts from the fundamentals.

## How to use

Invoke the skill by name, or run the script directly:

```bash
python scripts/audit-skill.py skills/my-skill --json
```

## Output

The skill produces a structured audit report with:

- Summary counts for blockers, warnings, and suggestions.
- Overall PASS / FAIL verdict.
- A findings table aligned with the rubric IDs.
- A remediation plan for failed checks.

## Directory layout

```
audit-skill/
├── SKILL.md
├── README.md
├── references/
│   └── AUDIT_RUBRIC.md
└── scripts/
    └── audit-skill.py
```

## Key conventions

- **Read-only:** the script does not modify the audited skill.
- **Deterministic where possible:** schema, file, and link checks are automated.
- **Heuristic checks marked manual:** quality judgments (e.g., description quality) are flagged for reviewer attention.
- **Rubric-aligned:** findings are labeled with the rubric IDs in `references/AUDIT_RUBRIC.md`.

## Maintenance notes

- Add new automated checks by extending the script.
- Update the rubric in `references/AUDIT_RUBRIC.md` when the standards evolve.
- Keep the output format stable so other tools can consume it.
