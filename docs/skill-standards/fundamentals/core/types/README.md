# Skill types

Most skills fall into one of three layers defined by the architecture:

- **Building block** — a narrow, reusable capability.
- **Conductor** — coordination of multiple skills or tools through phases.
- **Wrapper** — adaptation of another skill for human interaction.

A skill may participate in more than one layer, but its **primary role** should be clear. Choosing the wrong layer is the most common and expensive mistake in skill design.

---

## Deeper topics

- [`building-block.md`](./building-block.md) — narrow, reusable capabilities.
- [`conductor.md`](./conductor.md) — coordination and delegation.
- [`wrapper.md`](./wrapper.md) — user-facing adaptation.
- [`multi-layer-hybrid.md`](./multi-layer-hybrid.md) — skills that span more than one layer.
- [`choosing-a-type.md`](./choosing-a-type.md) — the decision tree for picking a type.
- [`type-migration.md`](./type-migration.md) — when and how a skill changes type.
- [`one-way-pattern-consistency.md`](./one-way-pattern-consistency.md) — one canonical way to solve each recurring problem.

---

## Granularity and splitting

How finely you divide skills matters. Each split spends one of two loads:

- More **model-invoked** skills spend **context load** — more descriptions crowding the window and competing for attention.
- More **user-invoked** skills spend **cognitive load** — more for the user to remember and reach for.

Two cuts guide splitting:

1. **By invocation** — split off a model-invoked skill when you have a distinct **leading word** that should trigger it on its own, or when another skill must reach it. The new description must earn its context load.
2. **By sequence** — split a run of steps when the later steps tempt the agent to rush the current step (**premature completion**). See [`../form-and-style/completion-criteria.md`](../form-and-style/completion-criteria.md) for how completion criteria and hidden post-completion steps cause premature completion. Keeping later steps out of view encourages the agent to do more legwork on the current task.

Beware the reverse: merging sequences exposes each step's post-completion steps to what follows, inviting premature completion.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
