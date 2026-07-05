---
name: parse-skill-frontmatter
description: Extract canonical frontmatter fields from a SKILL.md file.
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [frontmatter, parsing, building-block]
  verification_level: declared
  provenance:
    authored_by: mixed
    generated_by: agent
    origin: foreground
    reviewed_by: audit-skill
    reviewed_at: "2026-07-05T00:00:00Z"
    parent_session: write-a-skill-refactor
---

# parse-skill-frontmatter

## Purpose

Read a skill's `SKILL.md` and return the canonical frontmatter fields so other skills can consume skill metadata without reimplementing YAML parsing.

## Type

Building block.

## In scope

- Parse a single `SKILL.md` file.
- Extract `name`, `description`, `version`, `invocation`, and `metadata.tags`.
- Prefer PyYAML when available; fall back to a minimal regex parser.
- Return JSON or human-readable output.

## Out of scope

- Validating frontmatter against a schema.
- Writing files.
- Searching directories.

## When to use

Another skill or script needs to read skill metadata from a `SKILL.md` file.

## Steps

1. **Accept the `SKILL.md` path.**
   - **Completion criterion:** a resolved path is available.
2. **Read the file and locate the frontmatter block.**
   - **Completion criterion:** the YAML block between `---` fences is extracted.
3. **Parse the frontmatter.**
   - **Completion criterion:** canonical fields are extracted.
4. **Return the result.**
   - **Completion criterion:** JSON or human-readable output is emitted.

## Output format

With `--json`:

```json
{
  "name": "example-skill",
  "description": "An example skill.",
  "version": "1.0.0",
  "invocation": "model-invoked",
  "tags": ["example"]
}
```

## Security

- Read-only. No files are written or modified.
- Does not execute shell commands beyond the internal Python script.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- None.
