# challenge-assumptions

A deterministic building-block skill that stress-tests assumptions by searching for disproof signals across caller-provided evidence. It counters confirmation bias by looking for contradictions instead of confirmations.

## Files

- `SKILL.md` — Skill description, contract, and usage.
- `references/DEPENDENCIES.md` — Tools, binaries, and skill dependencies.
- `scripts/challenge-assumptions.py` — Deterministic entry point.
- `evals/evals.json` — Trigger and behavior tests.
- `README.md` — This file.

## Quick usage

```bash
python scripts/challenge-assumptions.py --help

echo '{"assumptions": [{"text": "Token refresh happens in auth.guard.ts."}], "evidence": {"codebase": "refresh is handled by refresh.interceptor.ts"}}' | python scripts/challenge-assumptions.py
```

## Input / output

- **Input**: JSON with `assumptions` (list of `{text, basis}`) and `evidence` (dict of strings or lists).
- **Output**: JSON with `status` and `assumptions` list (`{text, status, notes, disproof_refs}`).

See `SKILL.md` for the full contract.
