# Harness-specific example: Kimi Code CLI

This file is a harness-specific example for configuring the Jira tracker adapter with [Kimi Code CLI](https://kimi.com/). It is intentionally separate from the harness-agnostic tracker documentation so that Kimi-specific paths and configuration can be maintained without coupling other MCP clients to this setup.

## Jira MCP setup for Kimi Code CLI

Add the following server entry to `~/.kimi/mcp.json`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "cmd",
      "args": [
        "/c",
        "C:\\Users\\<username>\\AppData\\Roaming\\Python\\Python314\\Scripts\\mcp-atlassian.exe",
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

Replace `<username>` with your Windows user name and ensure the environment variables `JIRA_URL`, `JIRA_USERNAME`, and `JIRA_API_TOKEN` are set in the environment that Kimi Code CLI runs in.

## Other MCP clients

This is one example. Other MCP clients use the same `command`/`args`/`env` structure in their own MCP configuration format. Copy the same `command`, `args`, and `env` values into the equivalent client-specific configuration file.
