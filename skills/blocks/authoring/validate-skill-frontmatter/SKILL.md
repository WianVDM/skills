---
name: validate-skill-frontmatter
description: Validate SKILL.md YAML frontmatter against the skill-frontmatter JSON schema with line-level error reporting.
invocation: model-invoked

---

# validate-skill-frontmatter

## Purpose

Check that a `SKILL.md` file's YAML frontmatter conforms to the canonical `skill-frontmatter.schema.json`.

## Type

Building block.

## In scope

- Read a `SKILL.md` file.
- Extract the YAML frontmatter block.
- Validate the parsed frontmatter against `docs/skill-standards/schemas/skill-frontmatter.schema.json`.
- Report schema violations with line-level pointers where possible.

## Out of scope

- Validating the markdown body.
- Fixing the frontmatter.
- Writing files.

## When to use

- A skill author wants to confirm frontmatter correctness.
- `audit-skill` needs a full schema validation result.
- A CI pipeline enforces standards.

## Steps

1. **Accept the path to `SKILL.md` and optional schema path.**
   - **Completion criterion:** target and schema paths are resolved.
2. **Extract and parse the frontmatter YAML block.**
   - **Completion criterion:** the frontmatter object is loaded.
3. **Load the JSON schema.**
   - **Completion criterion:** the schema is available.
4. **Validate and collect errors.**
   - **Completion criterion:** all schema errors are captured.
5. **Return a structured report.**
   - **Completion criterion:** the report is emitted in the requested format.

## Output format

With `--json`:

```json
{
  "valid": true,
  "errors": []
}
```

Each error object contains:

- `message`: human-readable description.
- `path`: JSON pointer path in the frontmatter object.
- `line`: approximate line number in the original file, if available.

## Security

- Read-only. Does not modify the target file.
- Does not execute shell commands beyond the Python script.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `docs/skill-standards/schemas/skill-frontmatter.schema.json`
