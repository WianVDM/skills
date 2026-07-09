# scan-context

A building-block skill that discovers related context reports in a project's `{context_dir}/`. It matches by ticket key, project, branch, and report type, ranks results by relevance and freshness, and returns structured JSON.

## Usage

```bash
echo '{"context_dir": "/path/to/.agents/context", "ticket_key": "OC-4644"}' | python3 scripts/scan-context.py
```

## Files

- `SKILL.md` — skill contract and documentation.
- `scripts/scan-context.py` — deterministic scanner script.
- `evals/evals.json` — trigger and behavior tests.
- `references/DEPENDENCIES.md` — dependencies and requirements.
