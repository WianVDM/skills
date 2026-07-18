# Versioning

**Layer:** proposed architecture. **Mode:** rule.

Versioning matters when a skill has consumers — other skills, conductors, or external systems — that depend on its behavior or output schema. A versioned skill documents breaking changes, migration paths, and compatibility guarantees.

Versioning is not a fundamental. Simple, local skills do not need it. It is an architecture and library concern.

---

## When to version

Version a skill when:

- Other skills or conductors invoke it and depend on its output format.
- The skill produces context reports, schemas, or files that other skills consume.
- The skill is published or shared outside its origin project.
- The skill's config schema has consumers or migrators.

Do not version when:

- The skill is used only by you in one project.
- The output is only for human eyes.
- There are no consumers of its behavior or schema.

---

## What a version communicates

A version number is a promise about compatibility. It tells consumers whether they can continue using the skill without changes.

Use semantic meaning for version changes:

- **Major version bump** — breaking change. Consumers must update.
- **Minor version bump** — new capability, behavior, or schema field added. Existing consumers continue to work.
- **Patch version bump** — bug fix, clarification, or non-behavioral change. Existing consumers are unaffected.

The exact scheme is less important than consistency. Pick a scheme and document it.

---

## Breaking changes

A breaking change is any change that could cause an existing consumer to fail or produce incorrect results. Examples:

- Removing or renaming a field in a report schema.
- Changing the return format of a building-block skill.
- Removing a config key that consumers read.
- Changing the invocation contract or required arguments.
- Changing the meaning of an existing field without renaming it.

Non-breaking changes include:

- Adding new optional fields.
- Adding new steps that do not affect the output.
- Clarifying wording without changing behavior.
- Fixing a bug that consumers were relying on by mistake (this is breaking in practice, but sometimes unavoidable).

When in doubt, treat a change as breaking and bump the major version.

---

## Versioning policy

A versioned skill should document:

- The current version.
- The versioning scheme used.
- What kinds of changes are considered breaking.
- How long old versions are supported.
- How consumers migrate.

Document this in `references/VERSIONING.md` or in the `SKILL.md` body. The version itself lives in the package envelope:

```json
{
  "name": "context-reports",
  "version": "2.1.0",
  "skills": ["context-reports"]
}
```

---

## Migration paths

When a breaking change occurs, provide a migration path:

1. Document the old and new behavior.
2. Provide a mapping from old fields to new fields.
3. If possible, provide a migration script or helper.
4. Update consumers or notify their authors.
5. Keep the old behavior available for a deprecation period when practical.

For config schema changes, the initialization phase should handle migration automatically. See [`initialization.md`](./initialization.md) for migration guidance.

---

## Versioning for context reports

Context reports are a common source of breaking changes. If a report schema changes, every consumer of that report must be updated.

- Version the report schema separately from the skill version if consumers depend on the schema more than the skill.
- Include a `schema_version` field in the report so consumers can detect which version they are reading.
- Document the report schema in `references/CONTEXT_REPORTS.md`.

See [`context-reports.md`](./context-reports.md) for report contracts and schema guidance.

---

## Versioning for building blocks

Building blocks are invoked by other skills and conductors. Their outputs are the most likely source of breaking changes.

- Keep the output schema stable.
- If you must change the output, add new fields and deprecate old ones rather than removing them immediately.
- Declare the minimum and maximum supported versions of the building block in consumer dependencies.

---

## Versioning for conductors

Conductors coordinate multiple skills. Their versioning is usually less about output schema and more about workflow changes:

- Which phases exist and in what order.
- Which building blocks are invoked.
- What state is stored and where.

When a conductor changes its workflow, consumers (including users who rely on its behavior) may need to adapt. Document workflow changes clearly.

---

## Deprecation

Deprecation is the graceful removal of old behavior. A good deprecation process:

1. Mark the old behavior as deprecated in documentation.
2. Support both old and new behavior for a documented period.
3. Emit warnings when the old behavior is used.
4. Remove the old behavior only after the deprecation period ends.

Deprecation periods are a trade-off. Longer periods reduce consumer breakage; shorter periods reduce maintenance burden.

---

## Versioning checklist

- [ ] The skill has a documented version and versioning scheme.
- [ ] Breaking changes are clearly identified and bumped appropriately.
- [ ] Migration paths are documented for breaking changes.
- [ ] Report schemas are versioned if consumed by other skills.
- [ ] Consumers declare which versions they support.
- [ ] Deprecated behavior is documented and removed on a schedule.
- [ ] The versioning policy is stored in `references/VERSIONING.md` or the `SKILL.md` body.

---

## Related documents

- [`context-reports.md`](./context-reports.md) — report schema versioning.
- [`initialization.md`](./initialization.md) — config schema migration.
- [`building-block.md`](./building-block.md) — skills with consumers that need versioning.
- [`conductor.md`](./conductor.md) — workflow versioning.
- [`../fundamentals/core/lifecycle/`](../fundamentals/core/lifecycle/) — the full skill lifecycle including maintenance and retirement.

---

## Research basis

- The principle that **versioning matters when a skill has consumers** is a common denominator across the research. Codex, Claude Code, Hermes, and the agentskills.io ecosystem all support versioning at the package or skill level.
- The semantic meaning of major/minor/patch bumps is widely shared, though the exact definition of "breaking" varies by consumer. Our definition focuses on schema, output format, and invocation contract changes.
- The recommendation that **simple local skills do not need versioning** is our own, aligned with the philosophy that fundamentals are universal but architecture patterns are opt-in.
- **Report schema versioning** and **consumer version declarations** are our own practices, informed by the research on dependency management and composition.
- The **deprecation** guidance is our own synthesis of standard software deprecation practices.
