# Multi-layer and hybrid skills

**Layer:** proposed architecture. **Mode:** rule.

A skill may participate in more than one layer, but its primary role should be clear.

---

## Examples of multi-layer skills

- A **building block with a small workflow** — it does one narrow thing but has a few internal steps. Its primary role is still a building block.
- A **conductor that also produces a reusable report** — it coordinates work and produces a report that other skills consume. Its primary role is a conductor.
- A **hybrid skill** — it has its own core workflow and also embeds shared vocabulary from a building block. Its primary role depends on whether the main value is the workflow or the reusable vocabulary.

When a multi-layer skill grows, the boundary between layers becomes a seam. That is often the right time to split it:

- Extract the reusable vocabulary into a building block.
- Extract the coordination into a conductor.
- Extract the user interface into a wrapper.

---

## Common mistake

Using "hybrid" as an excuse for an unclear skill. If you cannot name the primary layer, the skill is not well-defined yet.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
