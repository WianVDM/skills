# Standards path

A skill must not hardcode a relative path to the canonical skill-standards wiki or to any other project convention that is not a declared dependency. It must resolve the `standards_path` through configuration, project-context detection, or explicit user consent, and it must disclose degraded behavior when the canonical docs are unavailable.

## Why this rule exists

Skill-standards docs can live in many places: `docs/skill-standards/` at the project root, `.agents/docs/skill-standards/`, `.pi/docs/skill-standards/`, a fetched bundle, or a global installation. A skill that embeds `../docs/skill-standards/` or similar assumptions breaks the moment the project uses a different layout or a different harness. It also makes the skill unusable in workspaces that install the standards separately from the repository.

This rule applies to any file referenced outside the skill that is not part of the declared dependency surface or a static, well-known convention.

## What is allowed

A skill may reference external locations when at least one of the following is true:

- The location is a **declared dependency** in `skills.json`, `references/DEPENDENCIES.md`, or `SKILL.md` frontmatter `depends`.
- The location is a **static, well-known convention** such as `{context_dir}/...` or `{config_dir}/...` where the variable is provided by `detect-project-context` or user config.
- The path is a **placeholder token** (e.g., `{chainlog_pattern_path}`) that the conductor resolves from the configured `standards_path` before the file is used.
- The path is resolved at runtime by a shared helper such as `resolve-standards-path.py`.

## What is not allowed

- Hardcoded relative paths like `../docs/skill-standards/`, `../../docs/skill-standards/`, `.agents/docs/skill-standards/`.
- Hardcoded sibling skill paths like `../other-skill/SKILL.md` or `../../blocks/other-skill/...` unless `other-skill` is declared as a dependency.
- Absolute paths to project or user directories in portable skill files.

## Resolution order

When a skill needs the canonical skill-standards path, resolve it in this order:

1. **Configured `standards_path`** — read from the skill's config (e.g., `write-a-skill.yaml`) or the user's global config.
2. **Project-context markers** — check `{marker}/docs/skill-standards/` for the detected marker (`.agents`, `.pi`, `agents`, etc.).
3. **Project-root defaults** — check `{project_root}/docs/skill-standards/`, then `{project_root}/.agents/docs/skill-standards/`, then `{project_root}/.pi/docs/skill-standards/`.
4. **Bundle default** — if the skill ships with a bundled copy of the standards, use that as a fallback.
5. **User prompt** — if none of the above are found, ask the user to provide the path or fetch the canonical docs.

## Lazy loading

A skill should resolve `standards_path` lazily:

- Detect it when the path is first needed, not at skill startup.
- Cache the resolved path in project state or the decision log for the current session.
- Re-detect only when the configured path is missing or the user asks to reinitialize.

## Degraded-mode disclosure

If the canonical standards cannot be resolved and the user declines to fetch or provide them, the skill must:

- Use any embedded fallback guidance it ships with.
- Tell the user which checks are reduced or skipped.
- Record the user's choice in the decision log.
- Offer to fetch or configure the path again later.

Use the degraded-mode template from [`tooling-awareness.md`](./tooling-awareness.md) or the project-specific handoff template.

## Enforcement

`audit-skill` checks this rule as `P-04` under **Portability**:

- It flags hardcoded relative paths to `docs/skill-standards` or similar project conventions.
- It flags markdown links that escape the skill directory and point to sibling skills not declared as dependencies.
- It allows placeholder tokens, declared dependencies, and paths resolved through `resolve-standards-path.py`.

## Shared resolver

Use the provided resolver script instead of reimplementing the resolution order:

- `skills/blocks/project/detect-project-context/scripts/resolve-standards-path.py`

The script returns JSON with `standards_path`, `status`, `source`, and `degraded`. Any skill can invoke it or wrap it as a building block.

## Common mistakes

- **Hardcoding standards links in static files.** If a static reference file must link to a standards doc, use a placeholder token that the conductor resolves, or omit the link and reference the doc by name.
- **Assuming the standards live at the project root.** Projects may keep standards under `.agents/docs/` or install them globally.
- **Resolving at skill startup.** Eager resolution makes the skill brittle when the standards are fetched later in the session.
- **Silent fallback.** If the canonical docs are missing, the user must know and consent to the degraded mode.

## Related documents

- [`tooling-awareness.md`](./tooling-awareness.md) — degradation disclosure and tool selection.
- [`dependencies-and-bundling.md`](./dependencies-and-bundling.md) — dependency declaration and lazy evaluation.
- [`../../patterns/context-reports.md`](../../patterns/context-reports.md) — shared artifacts and freshness rules.
- [`../../reference/audit-rubric.md`](../../reference/audit-rubric.md) — `P-04` and the portability checks.
- [`../../../skills/blocks/project/detect-project-context/scripts/resolve-standards-path.py`](../../../skills/blocks/project/detect-project-context/scripts/resolve-standards-path.py) — the shared resolver script.
