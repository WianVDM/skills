---
name: install-skill
description: Install a skill from a local path or archive URL into the project or user scope.
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [install, building-block]
  verification_level: declared
---

# install-skill

## Purpose

Install a skill from a known source into the project or user skill directory while confirming destructive-adjacent actions.

## Type

Building block.

## In scope

- Install from a local path.
- Install from an archive URL.
- Install into project scope or user scope.
- Record the install in `skills.json`.
- Confirm before overwriting an existing skill.

## Out of scope

- Searching for skills (use `search-skills-registry`).
- Installing from untrusted sources without explicit approval.
- Modifying the installed skill after installation.

## When to use

A conductor has identified a skill at a local path or archive URL and needs to make it available in the project or user scope.

## Steps

1. **Accept skill name, source, and target scope.**
   - **Completion criterion:** install parameters are resolved.
2. **Detect target directory.** Use `detect-project-context` for project scope or user-scope defaults.
   - **Completion criterion:** destination directory is identified.
3. **Resolve the source.** Look up the local path or archive URL.
   - **Completion criterion:** source is resolved to a copyable location.
4. **Confirm if the skill already exists or the source is untrusted.**
   - **Completion criterion:** user has approved the install, or the install is aborted.
5. **Copy the skill and update `skills.json`.**
   - **Completion criterion:** skill files are in the target directory and `skills.json` is updated.
6. **Return install report.**
   - **Completion criterion:** report with installed path is emitted.

## Output format

With `--json`:

```json
{
  "installed": true,
  "skill_name": "example-skill",
  "target_scope": "project",
  "installed_path": ".agents/skills/example-skill"
}
```

## Security

- Confirms before overwriting existing skills.
- Fails closed if the source is missing or untrusted.
- Records the install so the installed skill can be traced.
- Does not execute arbitrary install commands without user approval.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- None.
