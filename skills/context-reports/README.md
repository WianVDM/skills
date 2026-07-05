# context-reports

A vocabulary building block that provides the canonical conventions for shared context reports.

## When to use

Use this skill when:

- A skill produces or consumes context reports in a project.
- A skill author needs the canonical directory layout, report schema, freshness rules, or missing-report handling.
- A skill wants to declare which reports it consumes or produces in a standard way.

## How to use

A skill references this contract by:

1. Reading this skill's `SKILL.md` or invoking the `context-reports` skill.
2. Applying the shared directory layout, report envelope, and freshness rules.
3. Documenting skill-specific report types in its own `references/` or `SKILL.md`.

## Directory layout

```
context-reports/
├── SKILL.md
├── README.md
├── references/
│   └── DEPENDENCIES.md
└── evals/
    └── evals.json
```

## Key conventions

- **Reference, not workflow:** this skill defines shared conventions, not a process.
- **Type-organized directories:** reports live under `.agents/context/{report-type}/{key}.md`.
- **Frontmatter envelope:** reports include skill, version, key, generated_at, summary, and artifacts.
- **Freshness matters:** consumers validate timestamps and underlying source changes.
- **Missing reports are explicit:** required reports stop or consult the user; optional reports are noted.

## Maintenance notes

- Keep the schema and freshness rules in sync with `docs/skill-standards/patterns/context-reports.md`.
- Update the version when the report schema or freshness rules change.
- Add near-miss triggers to `evals/evals.json` if new report types could be confused with this skill.
