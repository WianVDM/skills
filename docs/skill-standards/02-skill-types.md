# 02 — Skill types

Most skills fall into one of four types. Choosing the right type is the single most important design decision.

| Type | Purpose | Loaded by default? | Typical size |
|------|---------|-------------------|--------------|
| **Standalone / Atomic** | One narrow job, complete in itself. | Sometimes | Very small |
| **Building-block / Vocabulary** | Shared language, rules, or principles other skills consume. | Sometimes | Small to medium |
| **Conductor / Orchestrator** | Coordinates other skills and subagents across phases. | Rarely | Medium to large |
| **Hybrid** | Core workflow plus embedded building blocks. | Sometimes | Medium |

A skill's type determines its structure, its invocation model, and how it relates to other skills.

---

## Granularity and splitting

How finely you divide skills matters. Each split spends one of two loads:

- More **model-invoked** skills spend **context load** — more descriptions crowding the window and competing for attention.
- More **user-invoked** skills spend **cognitive load** — more for the user to remember and reach for.

Two cuts guide splitting:

1. **By invocation** — split off a model-invoked skill when you have a distinct **leading word** that should trigger it on its own, or when another skill must reach it. The new description must earn its context load.
2. **By sequence** — split a run of steps when the steps ahead tempt the agent to rush the current step (**premature completion**). Keeping later steps out of view encourages the agent to do more legwork on the current task.

Beware the reverse: merging sequences exposes each step's post-completion steps to what follows, inviting premature completion.

---

## Standalone / Atomic

A standalone skill does one narrow job and needs little or no context from other skills to do it.

**When to use**

- The task is well-bounded.
- The model's priors are strong enough that extra structure adds noise.
- The skill is triggered by a clear user intent.

**Examples**

- A compressed-response skill that replies in ultra-short form.
- An interview skill that questions the user until shared understanding is reached.
- A conversation-summary skill that compacts the current conversation into a document.

**Characteristics**

- Usually user-invoked.
- Small and direct.
- Needs no state or minimal state.
- Often works as a single instruction or a short set of rules.

**Common mistake**

Turning an atomic skill into a workflow by adding phases, state, and references it does not need.

---

## Building-block / Vocabulary

A building-block skill provides shared language, rules, or reference material that other skills consume. It often does not do work itself; it shapes how other skills do work.

**When to use**

- A concept is reused across multiple skills.
- You want a single source of truth for a domain vocabulary or decision framework.
- The skill's value is in the language it provides, not in a sequence of actions.

**Examples**

- A code-style skill that defines shared vocabulary and rules for TypeScript.
- A config-pattern skill that defines how all skills load and persist configuration.
- A design-vocabulary skill that provides terms like deep module, seam, and public interface.

**Characteristics**

- Often model-invoked so other skills can reach it.
- Mostly reference, few or no steps.
- Consumed by standalone, conductor, and hybrid skills.
- Should not repeat material that belongs in a specific workflow skill.

**Common mistake**

Embedding building-block content inside every skill that needs it, creating duplication.

---

## Conductor / Orchestrator

A conductor skill coordinates other skills, subagents, or tools to run a multi-phase process. It does not do the deep work itself.

**When to use**

- The work is too large or cross-cutting for one skill.
- Sequencing matters and the agent would otherwise skip phases.
- State must be maintained across invocations or context compactions.

**Examples**

- A ticket-research skill that gathers ticket details and explores the codebase.
- A state-capture skill that records the current UI or system state before changes.
- A diagnosis skill that runs a hypothesis loop on a failing system.

**Characteristics**

- Usually user-invoked, sometimes model-invoked.
- Maintains state.
- Heavy delegation.
- Integrates findings from workers and other skills.

**Common mistake**

Doing the work inline instead of delegating, which bloats context and causes the agent to rush.

---

## Hybrid

A hybrid skill has its own core workflow but also embeds or consumes building-block skills. Most real skills are hybrids.

**When to use**

- The job needs both a clear process and a domain-specific vocabulary or decision framework.
- The workflow is sequential, but the decisions within it need principles.

**Examples**

- A ticket-debrief skill with a research workflow plus principles for confidence and scope.
- A test-driven-development skill with red-green-refactor cycles plus interface-design principles.
- A state-capture skill with a capture process plus rules for what to record and how to report it.

**Characteristics**

- Mixes steps and reference.
- Often uses progressive disclosure to keep the top level clean.
- May consume building-block skills for shared vocabulary.

**Common mistake**

Letting the reference overwhelm the steps, or vice versa. The two should be clearly separated.

---

## Choosing a type

Ask these questions in order:

1. Does this solve one narrow, well-bounded problem? → **Standalone**.
2. Is this primarily shared language or rules that other skills will reuse? → **Building-block**.
3. Does this coordinate multiple skills or subagents through phases? → **Conductor**.
4. Does it need both a workflow and embedded principles? → **Hybrid**.

If you cannot answer these clearly, the skill is probably not well-defined yet.

---

## Type migration

A skill's type can change as it matures:

- A standalone skill that grows multiple phases may become a hybrid.
- A hybrid skill whose main job becomes coordination may become a conductor.
- A piece of reference repeated across several skills may be extracted into a building-block skill.

When a skill changes type, its structure and invocation model should change too. Do not keep a user-invoked shell around a conductor's internals, or a model-invoked description on a skill that no longer needs discovery.
