# The four axes of skill design

**Layer:** universal fundamentals. **Mode:** explanation.

Skill design is the deliberate tuning of four axes. Each axis is a set of levers that makes the agent more predictable.

---

## 1. Invocation

How the skill is reached and the cost paid for that reach.

- **Model-invoked** skills keep their description, so the agent can fire them and other skills can reach them. They pay **context load**.
- **User-invoked** skills strip the description, so only the human can reach them by name. They pay **cognitive load**.

See [`../structure/frontmatter.md`](../structure/frontmatter.md) for invocation mode.

---

## 2. Information hierarchy

How the skill's content is arranged and how far down the ladder each piece sits.

- **In-skill steps** — ordered actions in `SKILL.md`.
- **In-skill reference** — definitions, rules, and facts in `SKILL.md`.
- **Disclosed reference** — material behind a context pointer in a sibling file.
- **External reference** — shared reference outside the skill system, reachable by any skill.

See [`../structure/progressive-disclosure.md`](../structure/progressive-disclosure.md) for progressive disclosure and the information hierarchy.

---

## 3. Steering

How the skill shapes the agent's runtime behavior.

- **Leading words** recruit priors the model already holds.
- **Completion criteria** tell the agent when a step is done.
- **Legwork** is the digging the agent does within a step.
- **Post-completion steps** are the later steps that tempt the agent to rush.

See [`../form-and-style/`](../form-and-style/) for steering levers.

---

## 4. Pruning

How the skill is kept lean and relevant.

- **Single source of truth** — one authoritative place for each meaning. See [`../common-mistakes/bloat.md#duplication`](../common-mistakes/bloat.md#duplication).
- **No-op test** — does this line change behavior versus the default? See [`../form-and-style/pruning.md`](../form-and-style/pruning.md).
- **Relevance** — does this line still bear on what the skill does? See [`../form-and-style/pruning.md`](../form-and-style/pruning.md).
- **Sediment** and **duplication** are the failure modes pruning prevents. See [`../common-mistakes/bloat.md`](../common-mistakes/bloat.md).

See [`../common-mistakes/`](../common-mistakes/) for failure modes and cures.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
