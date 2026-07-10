# Harness-agnostic language

Skills must not assume a specific agent harness, tool name, slash command, or vendor API.

| Bad | Good |
|-----|------|
| Run `/ticket OC-1234`. | Invoke the ticket-research skill for ticket OC-1234. |
| Call the `Agent` tool. | Spawn a focused worker. |
| Use `git status`. | Check the current working state. |
| Open Jira ticket PROJ-123. | Open the configured issue tracker for ticket PROJ-123. |
| Run `npm test`. | Run the project's test command. |

The skill should detect the environment, consult config, or ask the user.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
