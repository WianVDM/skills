# Composition test

The composition test exercises the script-based dependencies that `write-a-skill` delegates to. It creates a temporary sample skill and runs each script in sequence.

## Run the test

```bash
python skills/write-a-skill/scripts/composition-test.py
```

## What it tests

- `detect-project-context` — locates the project root and recommended directories.
- `list-available-skills` — discovers skills in the project scope.
- `parse-skill-frontmatter` — extracts canonical fields from a `SKILL.md`.
- `validate-skill-frontmatter` — validates frontmatter against the JSON schema.
- `audit-skill` — audits the sample skill with no blockers.
- `run-trigger-evals` — generates branch-aware trigger evals that pass schema validation.
- `chainlog` — verifies the `chainlog` building block exists and parses.
- `check-chainlog-needs` — verifies the chainlog classification subagent exists.
- chainlog templates — verifies all four `references/chainlog-template-*.md` files exist.
- chainlog audit fixture — verifies `audit-skill` reports `CL-02` for a consumer skill missing `artifact-freshness`.

## What it does not test

The conductor skills `decide-skill-shape` and `review-skill` are model-invoked and produce context reports. They are documented in the full workflow but are not invoked by this script.

## Expected output

```json
{
  "overall": "PASS",
  "results": [...]
}
```

The script exits with code `0` on success and `1` on failure.
