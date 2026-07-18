# Anti-patterns

**Layer:** universal fundamentals. **Mode:** rule.

These are common ways a skill's form or style goes wrong.

---

## Manual in disguise

A skill that lists every keystroke and command; the agent becomes a slow script executor. State intent, not mechanics, and use scripts for steps that must run exactly. See [`../common-mistakes/workflow-mistakes.md`](../common-mistakes/workflow-mistakes.md) for the full mistake and cure.

---

## Vague guideline soup

A skill that says many true things but gives the agent no purchase point, usually from weak or missing leading words and completion criteria. See [`../common-mistakes/weak-guidance.md`](../common-mistakes/weak-guidance.md) for the full mistake and cure, and [`../form-and-style/completion-criteria.md`](../form-and-style/completion-criteria.md) for checkable completion criteria.

---

## Over-constrained workflow

A skill that forces a rigid sequence where the domain has no natural sequence.

> Bad: A security review skill with ten mandatory steps in order.
>
> Better: A security review skill with a checklist the agent applies as it explores.

---

## Hidden hybrid

A skill that mixes steps and guidelines without signaling which is which. The agent cannot tell what is mandatory and what is advisory.

Use headings, numbering, and explicit wording to separate the two.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
