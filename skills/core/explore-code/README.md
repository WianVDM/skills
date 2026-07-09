# explore-code

A deterministic building-block skill that searches a codebase for evidence related to a ticket, question, or ambiguity.

## Purpose

`explore-code` answers: *"What does the codebase say about this?"* It finds mentioned files, comparable patterns, and relevant source/tests/ADRs, then returns a ranked list of evidence.

## Quick start

```bash
python3 skills/core/explore-code/scripts/explore-code.py <<'EOF'
{
  "ticket_summary": "Auth guard race condition during token refresh",
  "mentioned_files": ["src/app/guards/auth.guard.ts"],
  "task_type": "code",
  "max_files": 20
}
EOF
```

## Files

| File | Description |
|---|---|
| `SKILL.md` | Skill identity, purpose, contract, and usage notes. |
| `references/DEPENDENCIES.md` | Required tools, binaries, and skill dependencies. |
| `references/CONFIG_PATTERN.md` | Supported configuration keys and defaults. |
| `scripts/explore-code.py` | Deterministic entry point that reads JSON from stdin and returns JSON. |
| `evals/evals.json` | Trigger and behavior evaluation cases. |

## Dependencies

- Python 3.9+
- `ripgrep` (optional; Python fallback is always available)
- Harness tools: `read`, `ffgrep`, `fffind`, `bash`

## License

See project root LICENSE.
