# Conductor

A conductor skill coordinates other skills, subagents, or tools to run a multi-phase process. It does not do the deep work itself.

---

## When to use

- The work is too large or cross-cutting for one building block.
- Sequencing matters and the agent would otherwise skip phases.
- State must be maintained across invocations or context compactions.
- Multiple building blocks must be composed into a larger workflow.

---

## Examples

- `debrief` — gathers context, explores code, and writes a structured report.
- `orchestrate` — runs a project task from plan through implementation.
- `write-a-skill` — interviews the user, discovers existing skills, drafts a new skill, and runs an audit.

---

## Characteristics

- Usually **user-invoked**, sometimes **model-invoked** when the agent must coordinate autonomously.
- Maintains state and checkpoints.
- Heavy delegation to subagents and building blocks.
- Integrates findings from workers and other skills.
- Defines the workflow; the building blocks define the work.

---

## Common mistake

Doing the work inline instead of delegating, which bloats context and causes the agent to rush. A conductor is defined by orchestration, not by the number of tools it uses.

See [`../common-mistakes/tooling-and-shape-mistakes.md`](../common-mistakes/tooling-and-shape-mistakes.md) for wrong type for the job.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
