# Composition Test

The composition test exercises the `pr-report` conductor's wiring without requiring a live PR or external APIs.

## Run the test

```bash
python skills/workflow/pr-report/scripts/composition-test.py
```

## What it tests

- `SKILL.md` frontmatter validates against the JSON schema.
- `config.yaml` is parseable and declares the expected tooling keys.
- All internal markdown links in `SKILL.md`, `references/*.md`, and `subagents/*.md` resolve.
- `evals/evals.json` is valid and includes at least one behavioral eval.
- No adapter names remain in the skill files.

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

The script exits with code `0` on success and code `1` on failure.

## References

- `validate-skill-frontmatter` — frontmatter schema validation
- `audit-skill` — full fundamentals audit
- `eval-format` — eval schema conventions
