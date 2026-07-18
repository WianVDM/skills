---
name: search-skills-registry
description: Search configured skill registries for third-party skills that could cover a given need.
invocation: model-invoked
depends:
  - parse-skill-frontmatter
  - install-skill
---

# search-skills-registry

## Purpose

Find third-party skills that could help the user so that authors can reuse existing capabilities instead of building new ones.

## Type

Building block.

## In scope

- Load registry configuration from `.agents/config/write-a-skill.yaml` or use defaults.
- Search configured registries by natural-language query.
- Return structured results with source, description, trust signals, and install command.
- Handle offline or unavailable registries gracefully.

## Out of scope

- Installing skills (use `install-skill`).
- Evaluating the quality or security of third-party skills (report trust signals only).
- Writing files.

## When to use

A conductor needs to explore external alternatives before recommending a new skill.

## Registry configuration

See [`references/REGISTRY_CONFIGURATION.md`](references/REGISTRY_CONFIGURATION.md) for registry declaration format, supported `source_type` values, and built-in defaults.

## Steps

1. **Accept query and optional registry filter.**
   - **Completion criterion:** query is captured and registry filter is resolved.
2. **Load configuration.** Read `.agents/config/write-a-skill.yaml` or use built-in defaults.
   - **Completion criterion:** registry list is available.
3. **Search each registry.** Use the appropriate transport for each `source_type`.
   - **Completion criterion:** each registry returns results or a clear error.
4. **Normalize results.** Map each result to a common schema.
   - **Completion criterion:** results are normalized and deduplicated.
5. **Return structured report.** Emit JSON or human-readable output.
   - **Completion criterion:** the report is emitted in the requested format.

## Output format

With `--json`:

```json
{
  "query": "lint typescript",
  "registries": ["skills-sh", "npm"],
  "results": [
    {
      "source": "skills-sh",
      "name": "lint-ts",
      "description": "Lint TypeScript files with tsc and eslint.",
      "trust_signals": { "verified": true },
      "install_command": "install-skill lint-ts --source https://skills.sh/skills/lint-ts"
    }
  ],
  "errors": []
}
```

## Security

- Read-only. Does not install or modify anything.
- Network access is only used for registry searches.
- Fail closed if a registry source is untrusted or malformed.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [`references/REGISTRY_CONFIGURATION.md`](references/REGISTRY_CONFIGURATION.md) — registry declaration format and supported `source_type` values.
- [`references/INSTALL_COMMAND_FORMAT.md`](references/INSTALL_COMMAND_FORMAT.md) — expected install command format and invalid examples.
