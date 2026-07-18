# Pruning

**Layer:** universal fundamentals. **Mode:** rule.

A skill should be kept lean. Three disciplines help.

---

## Single source of truth

Each meaning should live in exactly one authoritative place. If a convention appears in multiple skills, extract it into a building-block skill or shared reference. Duplication inflates a concept's prominence and makes maintenance harder.

See [`../common-mistakes/bloat.md`](../common-mistakes/bloat.md) for duplication as a failure mode.

---

## Relevance

Does this line still bear on what the skill does? If a line is stale, off-topic, or belongs to a branch the skill no longer handles, remove it. A shorter skill is easier to keep relevant.

See [`../common-mistakes/bloat.md`](../common-mistakes/bloat.md) for sediment as a failure mode.

---

## Minimalism test

Remove one paragraph at a time from `SKILL.md`. If the skill still works, that paragraph was sediment. Prune it.

---

## No-op test

Run the **no-op test** on every line: *does this change behavior versus the default?* If the answer is no, the line is a no-op and should be deleted or replaced with a stronger leading word or completion criterion.

A line can be perfectly relevant and still be a no-op. "Be thorough" is relevant but usually a no-op. "Relentless" is a stronger leading word that passes the test.

This is model-relative: if you disagree whether a line is a no-op, settle it by running the skill, not by debate.

See [`../common-mistakes/weak-guidance.md`](../common-mistakes/weak-guidance.md) for no-op instructions as a failure mode and [`./leading-words.md`](./leading-words.md) for stronger leading words.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
