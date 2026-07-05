# Pattern hints (condensed)

> **This is a condensed fallback.** The canonical pattern documents live in `docs/skill-standards/patterns/`. If that directory is available, prefer it and treat this file as a degraded copy for projects that ship without the full standards wiki.

Use these decision rules to decide which Layer 2 architecture patterns apply to a skill.

| Pattern | Use when | Skip when |
|---|---|---|
| **Global / pluggable** | The skill must work in any project or harness. | The skill is project-specific and always will be. |
| **Configurable** | The skill needs per-project or per-user preferences. | The skill needs no preferences beyond detection. |
| **Initialization** | The skill is global/configurable and needs first-run setup. | The skill is stateless and needs no setup. |
| **Stateful** | The skill must survive context compaction or multi-session work. | The skill is fully stateless. |
| **Context reports** | The skill produces structured artifacts consumed by other skills. | The skill has no shared outputs. |
| **Versioning** | Other skills or consumers depend on the skill's behavior or schema. | The skill has no consumers and no schema contract. |
| **Discipline skill** | The skill enforces a rule that the model would otherwise rationalize around. | The rule is optional advice, not a guardrail. |
| **Context-file** | The guidance should be always-on and has no clear trigger. | There is a clear on-demand workflow. |
| **Mode** | The user wants a transient behavior switch. | The behavior should be encoded persistently in the skill. |
| **Conductor/implementer split** | The skill needs to separate reasoning from execution. | The skill is small enough to reason and execute inline. |

## Default starting point

1. Start with a **building block** if the skill does one narrow thing.
2. Promote to a **conductor** if it coordinates multiple skills or tools.
3. Add a **wrapper** only if a human-facing layer is needed.
4. Apply Layer 2 patterns only after the core shape is clear.

## Canonical source

For the full, maintained version of these patterns, see `docs/skill-standards/patterns/`:

- `building-block.md`
- `conductor.md`
- `wrapper.md`
- `discipline-skill.md`
- `context-file.md`
- `mode.md`
- `conductor-implementer-split.md`
- `global-pluggable.md`
- `configurable.md`
- `initialization.md`
- `stateful.md`
- `context-reports.md`
- `versioning.md`

Update this fallback only after the canonical docs change, and only to the minimum needed for self-contained operation.
