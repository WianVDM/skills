# map-ticket-relationships

Building-block skill that maps all relationships surrounding a ticket: parent, children, siblings, duplicates, linked tickets, blocked-by/blocks, implementation PRs/branches, original feature for bugs, attachments, and affected files.

Consumes normalized `ticket_data` from `research-ticket` and enriches it with local `git` inspection. Does not call tracker APIs in this first version.

## Files

- `SKILL.md` — full skill contract and design.
- `references/DEPENDENCIES.md` — tools, binaries, and skill dependencies.
- `references/CONFIG_PATTERN.md` — supported configuration keys.
- `scripts/map-ticket-relationships.py` — deterministic stdin/stdout JSON script.
- `evals/evals.json` — trigger and behavior tests.
- `README.md` — this summary.

## Quick usage

```bash
cat input.json | python3 scripts/map-ticket-relationships.py
```

See `SKILL.md` for the full input/output contract.
