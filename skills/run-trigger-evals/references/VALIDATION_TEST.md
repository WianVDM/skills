# Schema validation test

The generated `evals/evals.json` is validated against `docs/skill-standards/schemas/evals.json.schema.json` on every run. To prove the generation path passes schema validation, run:

```bash
python skills/run-trigger-evals/scripts/run-trigger-evals.py skills/audit-skill --json
```

Expected output:

```json
{
  "skill": "audit-skill",
  "valid": true,
  "errors": []
}
```

If `valid` is `true` and `errors` is empty, the generated evals conform to the schema.

To validate an existing `evals.json` without regenerating it:

```bash
python skills/run-trigger-evals/scripts/run-trigger-evals.py skills/audit-skill --validate --json
```
