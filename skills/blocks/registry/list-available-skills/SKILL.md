---
name: list-available-skills
description: Discover skills already available in the project and user scope by scanning canonical skill directories.
invocation: model-invoked
depends:
  - parse-skill-frontmatter
---

# list-available-skills

## Purpose

Produce a structured inventory of skills the current workspace already has access to, so that authors can reuse or extend existing capabilities instead of creating duplicates.

## Type

Building block.

## In scope

- Scan canonical project skill directories.
- Scan native harness skill directories for compatibility.
- Optionally scan the user-scope skill directory.
- Read each `SKILL.md` and extract frontmatter fields.
- Return a structured list with name, path, version, invocation, and depends.

## Out of scope

- Installing new skills.
- Searching external registries.
- Writing files.
- Asking the user questions.

## When to use

A conductor needs to know what skills already exist before recommending a new skill, reuse, or install.

## Steps

1. **Accept optional project root and user-scope flag.** Default to current working directory and include user scope.
   - **Completion criterion:** search roots and scope flags are determined.
2. **Build directory candidate list.** Include project and user canonical paths.
   - **Completion criterion:** candidate directories are collected.
3. **Scan for `SKILL.md` files.** Search one level deep inside each candidate directory.
   - **Completion criterion:** all discovered `SKILL.md` paths are recorded.
4. **Parse frontmatter.** Extract `name`, `description`, `invocation`, `version`, and `depends`.
   - **Completion criterion:** each discovered skill has a parsed record or an error entry.
5. **Return structured report.** Emit JSON or human-readable output.
   - **Completion criterion:** the report is emitted in the requested format.

## Output format

With `--json`:

```json
{
  "project_scope": ["skills/example-skill/SKILL.md"],
  "user_scope": ["~/.agents/skills/other-skill/SKILL.md"],
  "skills": [
    {
      "name": "example-skill",
      "path": "skills/example-skill",
      "invocation": "model-invoked",
      "version": "1.0.0"
    }
  ],
  "errors": []
}
```

`version` is omitted when it is not present in the skill's frontmatter.

## Security

- Read-only. No files are written or modified.
- Does not execute shell commands beyond the internal Python script.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- None.
