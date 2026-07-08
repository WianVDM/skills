# Composition Test

The composition test exercises the `pr-report` conductor's wiring without requiring a live PR or external APIs.

## Run the test

```bash
python skills/workflow/pr-report/scripts/composition-test.py
```

## What it tests

- `SKILL.md` frontmatter validates against the JSON schema.
- `config.yaml` is parseable and declares the required tooling keys.
- All internal markdown links in `SKILL.md` resolve.
- Built-in adapter registry entries point to existing skill directories.
- `evals/evals.json` is valid and includes at least one behavioral eval.

## What it does not test

- Live PR fetching from GitHub, CI providers, or static-analysis tools.
- Model-invoked routing and chat summaries.
- The `review-skill` and `write-a-skill` change/review gates.

## Expected output

```json
{
  "overall": "PASS",
  "results": [...]
}
```

The script exits with code `0` on success and `1` on failure.

## References

- `validate-skill-frontmatter` — frontmatter schema validation
- `audit-skill` — full fundamentals audit
- `eval-format` — eval schema conventions
