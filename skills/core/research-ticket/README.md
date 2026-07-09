# research-ticket

A building-block skill that fetches and normalizes ticket data from issue trackers (Jira, GitHub, Linear) or a manual fallback. It is invoked by conductors such as `debrief` and `pr-report` when they need tracker-agnostic ticket context before making decisions.

## What it does

- Reads a JSON request from stdin and writes a normalized JSON response to stdout.
- Dispatches to tracker-specific adapters (`jira`, `github`, `linear`) or a `manual` adapter.
- Returns core ticket fields, comments, attachments, history, development info, related tickets, worklog, and a context graph.
- Surfaces missing credentials or unrecoverable failures as `needs_input` or `blocked` without prompting the user directly.

## Files

- `SKILL.md` — skill identity, contract, adapters, and usage guidance.
- `references/DEPENDENCIES.md` — tools, binaries, and skill dependencies.
- `references/CONFIG_PATTERN.md` — tracker config schema.
- `scripts/research-ticket.py` — deterministic JSON-in/JSON-out helper.
- `evals/evals.json` — trigger, behavior, and pressure tests.
- `README.md` — this summary.

## Quick usage

```bash
python3 scripts/research-ticket.py < request.json
```

See `SKILL.md` for the full input/output contract and tracker configuration examples.
