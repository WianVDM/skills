# Initialization

Initialization is the first-run phase that prepares a global, configurable, or pluggable skill for use in a new project. It detects the environment, creates or migrates configuration, validates required capabilities, asks the user for required preferences, and writes initial notes.

Initialization is not a separate skill type. It is a phase that some skills run before their main work.

---

## When to use initialization

Use initialization when a skill needs to:

- Detect the project type, tooling, or conventions before doing work.
- Create a config file the first time it runs in a project.
- Ask the user for preferences that cannot be detected.
- Validate that required tools, environment variables, or skills are available.
- Migrate config from an older schema to a newer one.

Do not use initialization when:

- The skill is purely local and does not need config or state.
- Detection is trivial and can happen inline.
- The skill has no required preferences or external dependencies.

---

## Initialization contract

A good initialization phase is:

- **Explicit** — the user knows when it is running and why.
- **Idempotent** — running it twice does not corrupt state or create duplicates.
- **Fail-closed** — if a required capability is missing, it stops and explains.
- **Minimal** — it asks only for what it cannot detect or infer.
- **Observant** — it records what it detected and decided in notes.

---

## Initialization steps

A typical initialization flow:

1. **Detect environment**
   - Project type, package manager, test runner, issue tracker, VCS.
   - Existing config files or conventions.
   - Already-installed skills, tools, or extensions.

2. **Create or migrate config**
   - Write the default config file if it does not exist.
   - Read and migrate an existing config if the schema has changed.
   - Preserve user edits where possible.

3. **Ask for required preferences**
   - Ask only for values that cannot be detected or defaulted.
   - Explain why each preference is needed.
   - Offer sensible defaults.

4. **Validate capabilities**
   - Check that required tools are installed.
   - Check that required environment variables are set.
   - Check that required skills are available.
   - Stop and report any missing capability.

5. **Write initial notes**
   - Record what was detected.
   - Record decisions made during initialization.
   - Record any caveats or assumptions.

6. **Report readiness**
   - Tell the user what was configured.
   - List any remaining manual steps.
   - Confirm the skill is ready to use.

---

## Config location

Initialization should use the same config location as the configurable pattern:

```
{project-root}/.agents/config/
├── shared.yaml                # shared workspace settings
└── {skill-name}.yaml          # skill-specific config + notes
```

See [`configurable.md`](./configurable.md) for the config schema and notes convention.

---

## State and context location

Initialization may also create the skill's state directory if it is stateful:

```
{project-root}/.agents/context/{skill-name}/
└── {key}/
    ├── state.yaml
    └── artifacts/
```

See [`stateful.md`](./stateful.md) for state layout and checkpointing.

---

## Implementation

Initialization can be implemented:

- **Inline** in `SKILL.md` for simple cases (a few detection steps and one config file).
- **Via a script** in `scripts/initialize.{py,js,sh}` for complex detection or migration.
- **As a subagent** when the initialization requires exploration or judgment.

When using a script, the script should:

- Be deterministic and safe to run repeatedly.
- Return structured output indicating what was detected, created, and missing.
- Not perform destructive actions without confirmation.

---

## Idempotency

Initialization must be idempotent. If it runs twice:

- It should not create duplicate config files.
- It should not overwrite user edits unless the schema has changed.
- It should not re-ask the same questions if the answers are already stored.
- It should report that the skill is already initialized if nothing changed.

A common pattern is to check for the existence of a config file or a marker and skip initialization if it is already complete.

---

## Migration

When a skill's config schema changes, initialization must handle migration:

1. Detect the old schema version.
2. Map old keys to new keys.
3. Preserve values that still apply.
4. Ask the user for any new required values.
5. Write the migrated config and note the migration.

Document the migration path in `references/VERSIONING.md` or `references/CONFIG_PATTERN.md`.

---

## Security during initialization

- Never write secrets to config files during initialization.
- Ask the user to set environment variables or use a secure store for secrets.
- Do not run arbitrary commands from project files without inspection.
- Validate the source of any external data used during initialization.

See [`../fundamentals/security.md`](../fundamentals/security.md) for the full security rules.

---

## Initialization checklist

- [ ] Detection is explicit and well-scoped.
- [ ] Config creation is idempotent.
- [ ] The user is asked only for values that cannot be detected or defaulted.
- [ ] Required capabilities are validated.
- [ ] Missing capabilities are reported clearly with fail-closed behavior.
- [ ] Initial notes record what was detected and decided.
- [ ] The user receives a clear readiness report.
- [ ] No secrets are written to config files.
- [ ] Migration path is documented if the schema changes.

---

## Research basis

- The **initialization** pattern as a first-run phase for global and configurable skills is our own design choice, but it is strongly supported by the research finding that pluggable skills need to detect the environment, create config, and validate capabilities before doing their main work.
- The initialization contract (explicit, idempotent, fail-closed, minimal, observant) is our own synthesis of safe setup practices.
- The initialization steps (detect, create/migrate config, ask for preferences, validate capabilities, write notes, report readiness) are our own workflow.
- The recommendation to implement initialization inline, via script, or as a subagent depending on complexity is our own practice.
- The relationship between initialization, the **configurable** pattern, and the **stateful** pattern is documented in those respective files and in [docs/ARCHITECTURE.md](../../ARCHITECTURE.md).
---

## Related documents

- [`configurable.md`](./configurable.md) — config schema and notes convention.
- [`stateful.md`](./stateful.md) — state layout and checkpointing.
- [`global-pluggable.md`](./global-pluggable.md) — pluggability requirements that drive initialization.
- [`versioning.md`](./versioning.md) — schema migration and version policies.
- [`../fundamentals/security.md`](../fundamentals/security.md) — security rules during initialization.
