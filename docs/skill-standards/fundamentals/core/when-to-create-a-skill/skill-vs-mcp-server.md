# Skill vs MCP server

An MCP server exposes a structured interface to an external system. A skill guides how the agent uses tools.

| Use an MCP server | Use a skill |
|-------------------|-------------|
| Query a database. | Decide what queries to run and how to interpret results. |
| Create a GitHub issue. | Decide how to break a plan into issues. |
| Read from a browser. | Decide what pages to visit and what to capture. |

A skill may invoke an MCP server. An MCP server should not contain skill logic.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
