# Script curation

For general guidance on when to use scripts, how to structure them, and script conventions, see the canonical standards:

- `docs/skill-standards/FORMAT.md`
- `docs/skill-standards/patterns/building-block.md`

## write-a-skill specific guidance

When a proposed skill is mostly deterministic, prefer a standalone script under `scripts/` and a thin `SKILL.md` wrapper that focuses on **when to invoke** the skill. The script owns the repeatable logic; the `SKILL.md` owns the routing, scope, and user-facing contract. The conductor should validate that the script is read-only unless destructive operations are explicitly designed and confirmed.
