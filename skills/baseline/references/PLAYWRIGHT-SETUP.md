# Playwright MCP Setup

> **Optional examples.** This guide shows example configurations for some common MCP-capable clients. The `baseline` skill works with any MCP client that can run the recommended Playwright MCP server; the exact config path and format depend on the client you use.

If no browser automation capability is available, the `baseline` skill can guide the user through configuring Playwright MCP.

---

## When to use this guide

Use this guide when the skill detects that:

- No browser automation MCP server is connected.
- No project-level Playwright or Cypress tooling is available.
- The user wants to enable UI verification.

---

## Server recommendation

The original `baseline` skill used:

```text
@executeautomation/playwright-mcp-server@latest
```

This remains the recommended default. Other options include Stagehand MCP, Puppeteer MCP, and Browser-tools MCP.

---

## Per-harness configuration

The exact config location and format depend on the harness or client. Ask the user which client they use, then provide the matching snippet.

### Kimi Code CLI

Add to `~/.kimi/mcp.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server@latest"]
    }
  }
}
```

### Claude Code

Add to `~/.claude/mcp.json` or project-level `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server@latest"]
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server@latest"]
    }
  }
}
```

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server@latest"]
    }
  }
}
```

### Other clients

Use the same `command`/`args` structure in the client's MCP configuration.

---

## Verification

After the user confirms the MCP server is configured, the skill should verify it by navigating to a simple URL detected from the project or provided by the user (for example, a local dev server).

- Success → proceed with baseline capture.
- Failure → stop and ask the user to check the MCP server output.

---

## Do not do this

- Do not write MCP config files without user confirmation.
- Do not assume the user wants Playwright MCP if another tool is already available.
- Do not proceed with baseline capture if verification fails.
