# Decision rules

Use these rules to recommend the right shape for a capability. These rules are a heuristic, not a rigid decision tree. The final recommendation should always be presented to the user with rationale and alternatives.

## Shapes

| Shape | Best for | Avoid when |
|---|---|---|
| **New skill** | Repeated, judgment-shaped tasks that need a reusable contract and can fire autonomously or by name. | The task is one-off, deterministic, or better handled by a script. |
| **Existing skill** | The problem is already covered by a local or third-party skill. | The existing skill is a poor fit or would require significant extension. |
| **Script** | Narrow, deterministic tasks that need repeatable, fast execution. | The task requires judgment, user interaction, or coordination. |
| **MCP server** | The task needs external tools, real-time data, or sandboxed execution. | The task is pure reasoning or does not need external capabilities. |
| **Context file** | Reference, configuration, or shared conventions that skills consume. | The task is behavior or process that should be invoked. |
| **Mode** | Always-on guidance or a persistent persona that shapes the agent's behavior. | The task is narrow, one-off, or needs a structured artifact. |

## Classification questions

Ask one question at a time when the answer shapes the recommendation:

1. Is this a repeated, judgment-shaped task?
2. Should it fire autonomously, or only when explicitly invoked?
3. Does it coordinate multiple tools or skills?
4. Is it always-on guidance, or on-demand?
5. Is the output a deterministic transformation, or domain-shaped judgment?
6. Is it tied to a specific framework or convention?

## Decision heuristics

- If the task is **repeated and judgment-shaped**, lean toward a **new skill**.
- If the task is **already covered**, lean toward **reusing an existing skill** or installing one.
- If the task is **narrow and deterministic**, lean toward a **script**.
- If the task needs **external tools or real-time data**, lean toward an **MCP server**.
- If the task is **reference or configuration**, lean toward a **context file**.
- If the task is **always-on guidance or a persona**, lean toward a **mode**.

## Always present alternatives

Even when the recommendation is clear, list one or two alternatives and explain the trade-off. This keeps the user in control and surfaces assumptions.
