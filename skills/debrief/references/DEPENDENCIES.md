# Dependencies

## Required skills

None. `debrief` does not require another skill to function.

## Recommended skills

- `baseline` — used to capture current UI, API, or code state when the ticket involves verifiable behavior. A baseline is recommended for most tickets; see [BASELINE-INTEGRATION.md](BASELINE-INTEGRATION.md) for how to decide when to skip it.

## Optional consumed context

The skill may read reports from `.agents/context/{type}/{key}.md` when the key matches the ticket or branch:

- `baseline` — `.agents/context/baseline/{scope}-{branch}.md` for current-state evidence.
- `handoff` — previous session context and decisions.
- `plan-next` — planned next steps and known constraints.
- Any other report whose filename or frontmatter `ticket` / `key` / `branch` matches the current ticket.

These reports are optional. The skill must handle their absence gracefully.

## Required capabilities

- Read and write the project filesystem (`.agents/config/` and `.agents/context/`).
- Inspect git state (branch name, commit hash).
- Access one issue tracker (Jira, GitHub, Linear) or receive manual context from the user.
- Optionally invoke the `baseline` skill workflow.

## Required tools

None by default. The skill may use any available tool listed in [CAPABILITIES.md](CAPABILITIES.md).

## Environment variables

The skill may reference environment variables through tracker config keys (e.g., `token_env`, `username_env`). It does not require specific variables by default.
