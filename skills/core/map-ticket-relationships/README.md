# map-ticket-relationships

Building-block skill that maps relationships surrounding a ticket: parent, children, siblings, duplicates, linked tickets, blocked-by/blocks, implementation artifacts, original feature for bugs, attachments, and affected files. It consumes normalized `ticket_data` from `research-ticket` and enriches it with local `git` inspection. This first version does not call tracker APIs.

See [`SKILL.md`](SKILL.md) for the full input/output contract and known limitations.

## Quick usage

```bash
cat input.json | python3 scripts/map-ticket-relationships.py
```
