# Choosing a type

**Layer:** proposed architecture. **Mode:** guide.

Ask these questions in order:

1. Does this solve one narrow, well-bounded problem? → **Building block**.
2. Does this coordinate multiple skills or tools through phases? → **Conductor**.
3. Does this adapt another skill for a human? → **Wrapper**.
4. Does it combine layers with a clear primary role? → **Multi-layer / hybrid**.

If you cannot answer these clearly, the skill is probably not well-defined yet. Do not write it until the shape is clear.

---

## Granularity and splitting

How finely you divide skills matters. Each split spends one of two loads:

- More **model-invoked** skills spend **context load** — more descriptions crowding the window and competing for attention.
- More **user-invoked** skills spend **cognitive load** — more for the user to remember and reach for.

Two cuts guide splitting:

1. **By invocation** — split off a model-invoked skill when you have a distinct **leading word** that should trigger it on its own, or when another skill must reach it. The new description must earn its context load.
2. **By sequence** — split a run of steps when the later steps tempt the agent to rush the current step (**premature completion**). See [`../../core/form-and-style/completion-criteria.md`](../../core/form-and-style/completion-criteria.md) for how completion criteria and hidden post-completion steps cause premature completion. Keeping later steps out of view encourages the agent to do more legwork on the current task.

Beware the reverse: merging sequences exposes each step's post-completion steps to what follows, inviting premature completion.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
