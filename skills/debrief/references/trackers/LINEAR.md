# Linear Tracker Adapter

Adapter for fetching ticket context from Linear.

## Detection

Linear is available if any of the following are true:

- A `linear` MCP server is configured and responds.
- `LINEAR_API_KEY` env var is set.

## Capabilities

- Fetch issue details, comments, labels, state.
- Fetch related issues and cycles.
- Fetch linked PRs and commits.

## Config schema

```yaml
preferences:
  issue_tracker: linear
  trackers:
    linear:
      team_key: ENG
      token_env: LINEAR_API_KEY
```

## Authentication

Use env var references:

```yaml
token_env: LINEAR_API_KEY
```

## Setup guide

If no Linear MCP server is configured, guide the user to set one up. The required pieces are:

- **MCP server command** — an executable that speaks the MCP protocol over stdio (or SSE if the client supports it).
- **Environment variables** — the server typically needs `LINEAR_API_KEY`.
- **MCP server name** — register it with the name `linear` (or update `mcp_server_name` in config).

A generic client configuration looks like this:

```json
{
  "mcpServers": {
    "linear": {
      "command": "mcp-linear",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "LINEAR_API_KEY": "${LINEAR_API_KEY}"
      }
    }
  }
}
```

Replace the command, args, and env var names with whatever your MCP server and client require.

## Verification

Verify by fetching the team's issues or a specific issue.

## Mapping to debrief schema

| Linear field | Debrief field |
|--------------|---------------|
| `identifier` | `key` |
| `title` | `summary` |
| `description` | `description` |
| `state.name` | `status` |
| `priority` | `priority` |
| `assignee` | `assignee` |
| Comments | `discussion_summary` |
| Linked PRs | `development_context` |

## Limitations

- Linear uses team-based identifiers.
- Some features like components may not exist.
