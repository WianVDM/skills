# Eval format

`evals/evals.json` follows the canonical evaluation artifact schema:

```json
{
  "version": "1",
  "skill": "example-skill",
  "tests": [
    {
      "id": "should-trigger-01",
      "type": "trigger",
      "category": "should-trigger",
      "prompt": "User prompt that should invoke the skill.",
      "expected": "example-skill"
    },
    {
      "id": "should-not-trigger-01",
      "type": "trigger",
      "category": "should-not-trigger",
      "prompt": "User prompt that should not invoke the skill."
    }
  ]
}
```

## Fields

- `version`: schema version. Current value is `"1"`.
- `skill`: the canonical skill name from `SKILL.md` frontmatter.
- `tests`: a list of test cases. Each test case has:
  - `id`: unique test identifier.
  - `type`: `"trigger"` for routing tests.
  - `category`: `"should-trigger"` or `"should-not-trigger"`.
  - `prompt`: the user prompt used to test routing.
  - `expected`: the expected skill name for `should-trigger` cases; omitted for `should-not-trigger` cases.

## Validation

Generated evals are validated against `docs/skill-standards/schemas/evals.json.schema.json` when `jsonschema` is installed.
