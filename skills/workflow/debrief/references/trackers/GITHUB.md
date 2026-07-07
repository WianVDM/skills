# GitHub Issues Tracker Adapter

Adapter for fetching ticket context from GitHub Issues.

## Detection

GitHub is available if any of the following are true:

- A `github` MCP server is configured and responds.
- `GITHUB_TOKEN` env var is set.

## Capabilities

- Fetch issue details, comments, labels, assignees.
- Fetch linked PRs and commits.
- Fetch repository context.

## Config schema

```yaml
preferences:
  issue_tracker: github
  trackers:
    github:
      repo: owner/repo
      token_env: GITHUB_TOKEN
```

## Authentication

Use env var references:

```yaml
token_env: GITHUB_TOKEN
```

## Setup guide

If no GitHub MCP server is configured, guide the user to set one up. The required pieces are:

- **MCP server command** — an executable that speaks the MCP protocol over stdio (or SSE if the client supports it). A common choice is `@modelcontextprotocol/server-github`.
- **Environment variables** — the server typically needs `GITHUB_TOKEN`.
- **MCP server name** — register it with the name `github` (or update `mcp_server_name` in config).

A generic client configuration looks like this:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Replace the command, args, and env var names with whatever your MCP server and client require.

## Verification

Verify by fetching a known issue or the repository details.

## Mapping to debrief schema

| GitHub field | Debrief field |
|--------------|---------------|
| `number` | `key` |
| `title` | `summary` |
| `body` | `description` |
| `state` | `status` |
| `labels` | `labels` |
| `assignees` | `assignee` |
| Comments | `discussion_summary` |
| Linked PRs | `development_context` |

## Limitations

- GitHub Issues may not have all the metadata Jira provides.
- Project keys are not used; issue numbers are global per repo.
