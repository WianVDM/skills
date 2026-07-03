# Dependencies

## Required skills

None. `debrief` does not require another skill to function.

## Soft default building block

- `baseline` — used to capture current UI, API, or code state when the ticket involves verifiable behavior. Baseline is a soft default building block: invoke it when relevant, but the user must approve proceeding without it. See [BASELINE-INTEGRATION.md](BASELINE-INTEGRATION.md).

## Optional consumed context

The skill may read reports from `{context_dir}/{type}/{key}.md` when the key matches the ticket or branch:

- `baseline` — `{context_dir}/baseline/{scope}-{branch}.md` for current-state evidence.
- `handoff` — previous session context and decisions.
- `plan-next` — planned next steps and known constraints.
- Any other report whose filename or frontmatter `ticket` / `key` / `branch` matches the current ticket.

These reports are optional. The skill must handle their absence gracefully.

## Required capabilities

- Read and write the project filesystem (`{marker_dir}/config/` and `{context_dir}/`).
- Access one issue tracker (Jira, GitHub, Linear) or receive manual context from the user.
- Optionally inspect git state (branch name, commit hash) if git is available.
- Optionally invoke the `baseline` skill workflow.

## Required tools

None by default. The skill may use any available tool listed in [CAPABILITIES.md](CAPABILITIES.md).

## Environment variables

The skill may reference environment variables through tracker config keys (e.g., `token_env`, `username_env`). It does not require specific variables by default.
