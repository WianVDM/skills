# Dependencies

## Required skills

- `context-reports` — shared context-report conventions.
- `worker-contract` — canonical return contract.
- `research-ticket` — provider of normalized `ticket_data` consumed by this skill.

## Required tools and capabilities

- `read` — to consume input documents and references.
- `bash` — to run the deterministic Python script and `git` commands.
- Python 3.x — the script is written in Python and uses the standard library.

## Required binaries

- `python3` (or equivalent Python 3 interpreter).
- `git` — required for discovering branches and commits that mention the ticket key.

## Required MCP servers

None. This version does not call tracker APIs.

## Environment variables

None required. If a future version adds tracker API calls, token env vars will be referenced through `tracker_config`, not hardcoded.

## Optional dependencies

- `gh` (GitHub CLI) — may be used in a future version to list PRs locally. Not required for v1.0.0.
