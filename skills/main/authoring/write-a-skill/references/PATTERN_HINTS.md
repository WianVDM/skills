# Pattern hints (condensed)

> **This is a condensed fallback.** The canonical pattern documents live in `docs/skill-standards/patterns/`. If that directory is available, prefer it and treat this file as a degraded copy for projects that ship without the full standards wiki.
> Last synced: 2026-07-18 (source ref: faf4e5f).

Use these decision rules to decide which Layer 2 architecture patterns apply to a skill.

| Pattern | Use when | Skip when |
|---|---|---|
| **Global / pluggable** | The skill must work in any project or harness. | The skill is project-specific and always will be. |
| **Configurable** | The skill needs per-project or per-user preferences. | The skill needs no preferences beyond detection. |
| **Initialization** | The skill is global/configurable and needs first-run setup. Check required capabilities eagerly; evaluate recommended/optional capabilities lazily per method or branch to avoid upfront setup overload. | The skill is stateless and needs no setup. |
| **Stateful** | The skill must survive context compaction or multi-session work. | The skill is fully stateless. |
| **Context reports** | The skill produces structured artifacts consumed by other skills. | The skill has no shared outputs. |
| **Versioning** | Other skills or consumers depend on the skill's behavior or schema. | The skill has no consumers and no schema contract. |
| **Discipline skill** | The skill enforces a rule that the model would otherwise rationalize around. | The rule is optional advice, not a guardrail. |
| **Context-file** | The guidance should be always-on and has no clear trigger. | There is a clear on-demand workflow. |
| **Chainlog** | The skill collects or consumes observable data other skills could reuse. | The skill has no reusable observations. |
| **Portability** | The skill must run across harnesses, including minimal ones. | The skill only ever runs in one harness. |
| **Mode** | The user wants a transient behavior switch. | The behavior should be encoded persistently in the skill. |
| **Conductor/implementer split** | The skill needs to separate reasoning from execution. | The skill is small enough to reason and execute inline. |

## Pattern adherence is not optional

Patterns in this file and in the canonical `docs/skill-standards/patterns/` directory are load-bearing architecture decisions, not suggestions. When you select a pattern for a skill:

1. Cite the canonical source document.
2. Apply the pattern fully. A partial or "light" application is a deviation and must be recorded.
3. If you deviate, justify it: explain what behavior would break or what cost would be imposed by following the pattern exactly.
4. If the canonical docs are unavailable, use the degraded-mode warning template from [references/PLUGGABILITY.md](PLUGGABILITY.md) and fall back to this condensed guidance.

Do not treat patterns as a menu of optional conveniences. Treat them as constraints that shape the skill correctly.

## Default starting point

1. Start with a **building block** if the skill does one narrow thing.
2. Promote to a **conductor** if it coordinates multiple skills or tools.
3. Add a **wrapper** only if a human-facing layer is needed.
4. Apply Layer 2 patterns only after the core shape is clear.

## Capability matrix

For every load-bearing capability, document:

- The outcome needed.
- The preferred tool if available.
- The fallback tool(s).
- The degraded-output disclosure if the fallback is used.
- The user-consent prompt or preference key.

## Canonical source

For the full, maintained version of these patterns, see `docs/skill-standards/patterns/`:

<!-- BEGIN GENERATED: pattern-inventory -->
- `building-block.md`
- `chainlog.md`
- `conductor-implementer-split.md`
- `conductor.md`
- `configurable.md`
- `context-file.md`
- `context-reports.md`
- `discipline-skill.md`
- `global-pluggable.md`
- `initialization.md`
- `portability.md`
- `stateful.md`
- `versioning.md`
- `wrapper.md`
<!-- END GENERATED: pattern-inventory -->

The `mode` pattern's canonical doc lives outside `patterns/` at `docs/skill-standards/fundamentals/architecture/mode.md`.

Update this fallback only through `scripts/sync-fallbacks.py`, and only to the minimum needed for self-contained operation.
