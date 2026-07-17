# context-reports

A vocabulary building block that provides the canonical conventions for shared context reports.

## When to use

- A skill produces or consumes context reports in a project.
- A skill author needs the canonical directory layout, report envelope, freshness rules, or missing-report handling.
- A skill wants to declare which reports it consumes or produces in a standard way.

## How to use

1. Read the contract in [SKILL.md](SKILL.md) and the envelope in [references/SCHEMA.md](references/SCHEMA.md).
2. Apply the shared directory layout, envelope, and freshness rules.
3. Document skill-specific report types in the skill's own `references/` or `SKILL.md`.

## Directory layout

```text
context-reports/
├── SKILL.md
├── README.md
├── references/
│   ├── SCHEMA.md                     # envelope, repo conventions, declaration format
│   ├── context-report-schema.json    # embedded fallback mirror of the canonical schema
│   └── DEPENDENCIES.md
├── tests/
│   └── test_schema_sync.py           # keeps the mirror byte-identical to the canonical schema
└── evals/
    └── evals.json
```

## Key conventions

- **Reference, not workflow:** this skill defines shared conventions, not a process.
- **Type-organized directories:** reports live under `{context_dir}/{report-type}/{key}.md`.
- **Envelope:** reports carry `skill`, `key`, `generated_at`; `version`, `summary`, `artifacts` optional.
- **Canonical over fallback:** the skill-standards schema wins when resolvable; the local mirror is the fallback, kept byte-identical by the sync test.
- **Freshness is operational:** consumers use `artifact-freshness`; this block owns the rule, not the check.
- **Missing reports are explicit:** required reports stop or consult the user; optional reports are noted.

## Maintenance notes

- The canonical contract is the `context-reports` pattern in the skill-standards wiki; this skill adheres to it.
- If the canonical schema changes, update `references/context-report-schema.json` to match — the sync test fails until you do.
- Add near-miss triggers to `evals/evals.json` if new report types could be confused with this skill.
