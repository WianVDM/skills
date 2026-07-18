# What is a skill?

**Layer:** universal fundamentals. **Mode:** explanation.

A skill is the **smallest load-bearing shape** that makes an agent reliably do the right thing for a specific domain.

It is not:

- A script the agent executes word for word.
- A manual the agent reads before acting.
- A prompt the user types every time.
- A configuration file.

A skill is a **contract**. It tells the agent what matters, what to watch for, and what shape the work should take. The agent still decides the exact actions.

The most useful framing is that a skill is a **delegation boundary**: it lets a human or team say "here is how this kind of work is done here," and then have that guidance travel with the agent across sessions, tasks, and — when portable — harnesses.

---

## The root virtue: predictability

Every concept in these standards serves **predictability**: the agent should follow the same *process* every time the skill runs, even when the output varies. Cost, maintainability, and clarity are symptoms of it, not rivals.

See [`root-virtues.md`](./root-virtues.md) for the five virtues and the predictability test.

---

## Deeper topics

- [`design-axes.md`](./design-axes.md) — invocation, information hierarchy, steering, and pruning.
- [`root-virtues.md`](./root-virtues.md) — predictability, load-bearing minimalism, fit for purpose, composability, and explicitness.
- [`opposing-truths.md`](./opposing-truths.md) — tensions that run through skill design.
- [`when-it-fails.md`](./when-it-fails.md) — when to prune, split, or remove a skill.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
