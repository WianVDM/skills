# Dependencies

## Required tools

- `read`, `write`, `edit`, `bash` — core agent tools.

## Required binaries

- `git` — the skill is a git workflow and cannot function without it.
- `node` — required by the bundled helper scripts.
- `npm` — recommended for script diagnostics and running Node-based validation commands.

## Required skills

None. The skill delegates to subagents and scripts rather than consuming other skills.

## Recommended patterns

- `context-reports` — the skill produces structured merge reports that follow the context-reports conventions.
- `checkpoint` — the skill checkpoints state for resumption, which aligns with the checkpointing pattern.

## Optional MCP servers

- GitHub MCP — for PR metadata, commit context, and author info.
- Jira MCP — for ticket context from branch names.
- Linear MCP — for ticket context.
- Asana MCP — for ticket context.

A missing MCP server is not a hard stop; the skill falls back to git metadata and configured ticket adapters.

## Optional environment variables

- `GITHUB_TOKEN` — for GitHub MCP or private GitHub remotes.
- `JIRA_API_TOKEN` — for the Jira ticket adapter.
- `LINEAR_API_KEY` — for the Linear ticket adapter.
- `ASANA_ACCESS_TOKEN` — for the Asana ticket adapter.

## Required environment variables

None.
