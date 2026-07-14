# Decision rules

Use these rules to recommend the right shape for a capability. These rules are a heuristic, not a rigid decision tree. The final recommendation should always be presented to the user with rationale and alternatives.

## Shapes

| Shape | Best for | Avoid when |
|---|---|---|
| **New skill** | Repeated, judgment-shaped tasks that need a reusable contract and can fire autonomously or by name. | The task is one-off, deterministic, or better handled by a script. |
| **Existing skill** | The problem is already covered by a local or third-party skill, or by an existing tool, MCP server, or native binary that can fulfill the capability. | The existing option is a poor fit or would require significant extension. |
| **Script** | Narrow, deterministic tasks that need repeatable, fast execution. | The task requires judgment, user interaction, or coordination. |
| **MCP server** | The task needs external tools, real-time data, or sandboxed execution. | The task is pure reasoning or does not need external capabilities. |
| **Context file** | Reference, configuration, or shared conventions that skills consume. | The task is behavior or process that should be invoked. |
| **Mode** | Always-on guidance or a persistent persona that shapes the agent's behavior. | The task is narrow, one-off, or needs a structured artifact. |

## Classification questions

Ask one question at a time when the answer shapes the recommendation. These four questions replace the previous six-question interview to reduce token load while preserving signal.

1. **Repetition and judgment** — Is this a repeated, judgment-shaped task or a narrow, deterministic transformation?
   - Repeated + judgment → lean toward a **new skill**.
   - Narrow + deterministic → lean toward a **script**.
2. **Trigger mode** — Should it fire autonomously, only when explicitly invoked, or always be active?
   - Autonomous or by-name → lean toward a **skill**.
   - Always-on guidance or persona → lean toward a **mode**.
3. **Coordination scope** — Does it coordinate multiple tools or skills, or is it a single focused capability?
   - Coordinates multiple tools/skills → lean toward a **conductor** or **MCP server** if external tools are needed.
   - Single focused capability → lean toward a **building-block skill** or **script**.
4. **Artifact nature** — Is the output behavior, reference/configuration, or external tooling?
   - Behavior or process → lean toward a **skill** or **script**.
   - Reference or configuration → lean toward a **context file**.
   - External tooling or real-time data → lean toward an **MCP server**.

## Decision heuristics

- If the task is **repeated and judgment-shaped**, lean toward a **new skill**.
- If the task is **already covered by a skill, tool, MCP server, or native binary**, lean toward **reusing or extending that option** before creating a new skill.
- If the task is **narrow and deterministic**, lean toward a **script**.
- If the task needs **external tools or real-time data**, lean toward an **MCP server**.
- If the task is **reference or configuration**, lean toward a **context file**.
- If the task is **always-on guidance or a persona**, lean toward a **mode**.
- If the capability is **only used by one existing skill and is not cross-cutting**, lean toward **colocating** it inside that skill rather than extracting it.
- If the capability is **cross-cutting, has multiple current consumers, has a stable narrow interface, or solves a generic-domain problem**, lean toward **extracting** it as a new building-block skill.

## Colocation vs extraction

Before recommending a new skill, check whether the capability should simply live inside an existing skill.

**Colocate** when:
- Only one skill would use the capability.
- The capability is provider-specific or workflow-specific.
- The capability changes when the owning skill changes.
- The extraction would create a skill whose identity is framed around another skill as its consumer (e.g., "for the pr-report conductor").

**Extract** when:
- The capability is cross-cutting (e.g., token resolution, context reports, worker contracts).
- Two or more skills currently consume it.
- It has a stable, narrow interface that changes more slowly than its consumers.
- It solves a generic-domain problem rather than a workflow-specific problem.

A skill that exists only to serve one other skill is usually a submodule pretending to be a building block.

## Always present alternatives

Even when the recommendation is clear, list one or two alternatives and explain the trade-off. This keeps the user in control and surfaces assumptions.
