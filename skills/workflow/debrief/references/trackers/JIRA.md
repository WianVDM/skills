# Jira Tracker Adapter

Adapter for fetching ticket context from Jira.

## Detection

Jira is available if any of the following are true:

- A `jira` MCP server is configured and responds.
- `JIRA_URL`, `JIRA_USERNAME`, and `JIRA_API_TOKEN` env vars are set.

## Capabilities

- Fetch ticket details, comments, attachments, history.
- Download attachments and images.
- Get status transitions and time in status.
- Get linked PRs, branches, and commits.
- Get related issues (parent, subtasks, links).
- Get worklog entries.

## Config schema

```yaml
preferences:
  issue_tracker: jira
  trackers:
    jira:
      server_url: https://your-domain.atlassian.net
      username: your-email@example.com
      token_env: JIRA_API_TOKEN
      username_env: JIRA_USERNAME
      mcp_server_name: jira
```

## Authentication

Use env var references, not plaintext tokens:

```yaml
token_env: JIRA_API_TOKEN
username_env: JIRA_USERNAME
```

The actual values should live in the MCP server config or in the user's environment.

## Setup guide

If no Jira MCP server is configured, guide the user to set one up. The required pieces are:

- **MCP server command** — an executable that speaks the MCP protocol over stdio (or SSE if the client supports it). For example, a read-only Jira server might be started with `mcp-atlassian --transport stdio --read-only`.
- **Environment variables** — the server needs `JIRA_URL`, `JIRA_USERNAME`, and `JIRA_API_TOKEN`.
- **MCP server name** — register it with the name `jira` (or update `mcp_server_name` in config).

A generic client configuration looks like this:

```json
{
  "mcpServers": {
    "jira": {
      "command": "mcp-atlassian",
      "args": [
        "--transport",
        "stdio",
        "--read-only"
      ],
      "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_USERNAME": "${JIRA_USERNAME}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
      }
    }
  }
}
```

Replace the command, args, and env var names with whatever your MCP server and client require.

## Verification

After setup, verify connectivity by fetching the list of accessible projects.

## Mapping to debrief schema

| Jira field | Debrief field |
|------------|---------------|
| `key` | `key` |
| `fields.summary` | `summary` |
| `fields.description` | `description` |
| `fields.status.name` | `status` |
| `fields.priority.name` | `priority` |
| `fields.assignee` | `assignee` |
| `fields.reporter` | `reporter` |
| `fields.labels` | `labels` |
| `fields.components` | `components` |
| `fields.issuelinks` | `related_tickets` |
| Comments | `discussion_summary` |
| Attachments | `attachments_reviewed` |
| Changelog | `history` |

## Limitations

- Some Jira MCP servers may not expose all fields.
- Attachments may require separate download calls.
- Large comment threads may need truncation or summarization.
