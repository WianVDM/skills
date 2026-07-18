---
name: install-skill
description: Install a skill from a local path or archive URL into the project or user scope.
invocation: model-invoked
depends:
  - detect-project-context
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
   - The script does not prompt the user. Instead, it returns a `confirm before overwrite` result and the conductor owns the confirmation.
   - **Completion criterion:** user has approved the install, or the install is aborted.
5. **Copy the skill.**
   - **Completion criterion:** skill files are in the target directory.
6. **Return install report.**
   - **Completion criterion:** report with installed path is emitted.

## Confirmation contract

- The `--yes` flag is for non-interactive use only after the calling conductor has already obtained explicit user approval.
- If the skill already exists and `--yes` is not provided, the script returns a result with `"installed": false` and a reason asking for confirmation.
- The conductor must not pass `--yes` unless the user has explicitly approved the overwrite.

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

- Confirms before overwriting existing skills by returning a confirmation result, not by prompting.
- The conductor is responsible for obtaining explicit user approval before passing `--yes`.
- Fails closed if the source is missing or untrusted.
- Does not execute arbitrary install commands without user approval.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- None.
