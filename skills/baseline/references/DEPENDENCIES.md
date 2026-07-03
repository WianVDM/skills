# Dependencies

## Required skills

None. `baseline` is a standalone skill.

## Optional consumed context

The skill may scan and read reports from `.agents/context/{type}/{key}.md` when the `key` matches the scope, ticket, or branch. Common report types include:

- `debrief` — ticket understanding and expected behavior.
- `handoff` — previous session context and decisions.
- `plan-next` — planned next steps and known constraints.

These reports are optional. The skill must handle their absence gracefully.

## Required capabilities

- Inspect the current git state (branch, commit, working tree status).
- Detect at least one capture method or obtain user agreement for a manual fallback.

## Required tools

None, but the skill may use any available tool listed in [CAPABILITIES.md](CAPABILITIES.md).

## Environment variables

The skill may reference environment variables through config keys (e.g., `username_env`, `password_env` for authentication). It does not require specific variables by default.
