# research-ticket

A building-block skill that fetches and normalizes ticket data from issue trackers (Jira, GitHub, Linear) or a manual fallback. It returns a tracker-agnostic envelope that downstream skills such as `map-ticket-relationships` can consume.

See [`SKILL.md`](SKILL.md) for the full input/output contract, tracker configuration, and known limitations.

## Quick usage

```bash
python3 scripts/research-ticket.py < request.json
```

The script reads JSON from stdin and writes a normalized JSON response to stdout. It does not prompt the user directly; missing credentials are surfaced as `needs_input`.
