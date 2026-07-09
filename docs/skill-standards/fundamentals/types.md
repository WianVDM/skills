# Skill types

Most skills fall into one of three layers defined by the architecture:

- **Building block** — a narrow, reusable capability.
- **Conductor** — coordination of multiple skills or tools through phases.
- **Wrapper** — adaptation of another skill for human interaction.

A skill may participate in more than one layer, but its **primary role** should be clear. Choosing the wrong layer is the most common and expensive mistake in skill design.

---

## Granularity and splitting

How finely you divide skills matters. Each split spends one of two loads:

- More **model-invoked** skills spend **context load** — more descriptions crowding the window and competing for attention.
- More **user-invoked** skills spend **cognitive load** — more for the user to remember and reach for.

Two cuts guide splitting:

1. **By invocation** — split off a model-invoked skill when you have a distinct **leading word** that should trigger it on its own, or when another skill must reach it. The new description must earn its context load.
2. **By sequence** — split a run of steps when the later steps tempt the agent to rush the current step (**premature completion**). See [form-and-style.md](./form-and-style.md) for how completion criteria and hidden post-completion steps cause premature completion. Keeping later steps out of view encourages the agent to do more legwork on the current task.

Beware the reverse: merging sequences exposes each step's post-completion steps to what follows, inviting premature completion.

---

## Building block

A building block is a narrow skill that does one thing well and has a clear interface. It is the primary unit of reuse in the library.

A building block can be invoked by a human, by another skill, or by a conductor. Its defining trait is focus, not its consumer.

**When to use**

- The task is well-bounded.
- The skill provides a capability that could be reused by conductors or other skills.
- The output should be structured and predictable.

**Examples**

- `find-skills` — discovers available skills and returns structured results.
- `install-skill` — installs a skill given a name or source.
- `verify-skill` — checks a skill against the standards.
- `summarize-text` — compacts text into a specified format.

**Characteristics**

- Usually **model-invoked** if other skills or conductors need to reach it.
- Can be **user-invoked** if only humans use it directly.
- Small, focused `SKILL.md` with a clear contract.
- Declares dependencies explicitly.
- Produces structured output that consumers can act on.
- Avoids presentation, workflow, or coordination concerns.

**Common mistake**

Adding presentation logic, workflow phases, or heavy state management that belongs in a wrapper or conductor. A building block should stay narrow.

---

## Conductor

A conductor skill coordinates other skills, subagents, or tools to run a multi-phase process. It does not do the deep work itself.

**When to use**

- The work is too large or cross-cutting for one building block.
- Sequencing matters and the agent would otherwise skip phases.
- State must be maintained across invocations or context compactions.
- Multiple building blocks must be composed into a larger workflow.

**Examples**

- `debrief` — gathers context, explores code, and writes a structured report.
- `orchestrate` — runs a project task from plan through implementation.
- `write-a-skill` — interviews the user, discovers existing skills, drafts a new skill, and runs an audit.

**Characteristics**

- Usually **user-invoked**, sometimes **model-invoked** when the agent must coordinate autonomously.
- Maintains state and checkpoints.
- Heavy delegation to subagents and building blocks.
- Integrates findings from workers and other skills.
- Defines the workflow; the building blocks define the work.

**Common mistake**

Doing the work inline instead of delegating, which bloats context and causes the agent to rush. A conductor is defined by orchestration, not by the number of tools it uses.

---

## Wrapper

A wrapper skill is a thin layer that adapts a building block or conductor for human interaction. It adds prompts, presentation, confirmation, and user-facing language.

**When to use**

- A building block or conductor exists but needs user-facing prompts or confirmation.
- The user should see a curated summary rather than raw output.
- The workflow needs explicit human gates between phases.

**Examples**

- A find-and-install concierge that uses `find-skills` and `install-skill`.
- A report viewer that presents a `debrief` report in a concise format.
- A confirmation gate before a destructive building block runs.

**Characteristics**

- Usually **user-invoked** because its primary consumer is the human. May be model-invoked only when the harness explicitly supports it and the use case requires autonomous routing.
- Thin: no core logic that belongs in the wrapped skill.
- Focused on prompts, presentation, and confirmation.
- May act as a router, naming several related skills and when to reach for each.

**Common mistake**

Letting the wrapper grow into a conductor by adding phases, state, or complex coordination. If that happens, promote it to a conductor.

See [`../patterns/wrapper.md`](../patterns/wrapper.md) for the full wrapper pattern.

---

## Multi-layer / hybrid skills

A skill may participate in more than one layer, but its primary role should be clear.

**Examples of multi-layer skills**

- A **building block with a small workflow** — it does one narrow thing but has a few internal steps. Its primary role is still a building block.
- A **conductor that also produces a reusable report** — it coordinates work and produces a report that other skills consume. Its primary role is a conductor.
- A **hybrid skill** — it has its own core workflow and also embeds shared vocabulary from a building block. Its primary role depends on whether the main value is the workflow or the reusable vocabulary.

When a multi-layer skill grows, the boundary between layers becomes a seam. That is often the right time to split it:

- Extract the reusable vocabulary into a building block.
- Extract the coordination into a conductor.
- Extract the user interface into a wrapper.

**Common mistake**

Using "hybrid" as an excuse for an unclear skill. If you cannot name the primary layer, the skill is not well-defined yet.

---

## Choosing a type

Ask these questions in order:

1. Does this solve one narrow, well-bounded problem? → **Building block**.
2. Does this coordinate multiple skills or tools through phases? → **Conductor**.
3. Does this adapt another skill for a human? → **Wrapper**.
4. Does it combine layers with a clear primary role? → **Multi-layer / hybrid**.

If you cannot answer these clearly, the skill is probably not well-defined yet. Do not write it until the shape is clear.

---

## Type migration

A skill's primary layer can change as it matures:

- A building block that grows workflow phases may become a conductor.
- A conductor whose value is mostly a reusable report may split into a conductor and a building block.
- A wrapper that starts coordinating multiple skills may become a conductor with a thin wrapper on top.
- A piece of reference repeated across several skills may be extracted into a building block.

When a skill changes type, its structure and invocation model should change too. Do not keep a user-invoked shell around a conductor's internals, or a model-invoked description on a skill that no longer needs discovery.

---

## One-way pattern consistency

A reusable skill should encode exactly one canonical way to solve each recurring problem. When a skill offers multiple valid approaches, the agent faces decision paralysis and output becomes inconsistent.

| Inconsistent skill | Consistent skill |
|--------------------|------------------|
| "Use either classes or factory functions." | "Use factory functions for create-X helpers." |
| "Return errors or throw, whichever you prefer." | "Throw for programmer errors; return `Result` for expected failures." |
| "Use mocks or stubs as needed." | "Use stubs for dependencies; avoid mocking internal functions." |

One-way consistency does not mean ignoring context. It means the skill makes the default choice explicit and explains when to deviate.

---

## Related documents

- [`../patterns/building-block.md`](../patterns/building-block.md) — reusable skills in depth.
- [`../patterns/conductor.md`](../patterns/conductor.md) — coordination and delegation in depth.
- [`../patterns/wrapper.md`](../patterns/wrapper.md) — user-facing adaptation in depth.
- [`../patterns/discipline-skill.md`](../patterns/discipline-skill.md) — anti-rationalization and pressure-testing patterns.
- [`../patterns/context-file.md`](../patterns/context-file.md) — always-on guidance that is not a skill.
- [`../patterns/mode.md`](../patterns/mode.md) — transient behavior switches.
- [`../patterns/conductor-implementer-split.md`](../patterns/conductor-implementer-split.md) — separating reasoning from execution.
- [`./structure.md`](./structure.md) — invocation mode and `SKILL.md` structure.
- [`./when-to-create-a-skill.md`](../start/when-to-create-a-skill.md) — when to create a skill instead of a script, MCP, or prompt template.
- [`./common-mistakes.md`](./common-mistakes.md) — splitting, bloat, and premature completion.

---

## Research basis

See [SOURCES.md](../reference/sources.md).
