# Anti-patterns

These are common ways a skill's form or style goes wrong.

---

## Manual in disguise

A skill that lists every keystroke and command. The agent becomes a slow script executor.

> Bad: "Run `git status`, then `git diff`, then `git log --oneline -5`."
>
> Better: "Understand the current working state before making changes."

State intent, not mechanics. Use scripts for deterministic steps that must be repeated exactly.

See [`../common-mistakes/workflow-mistakes.md`](../common-mistakes/workflow-mistakes.md) for the manual-in-disguise mistake.

---

## Vague guideline soup

A skill that says many true things but gives the agent no purchase point. Often caused by weak or missing leading words and completion criteria.

> Bad: "Be thorough. Consider edge cases. Write good tests."
>
> Better: "For each public behavior, write one test through the public interface. Stop when the user confirms the listed behaviors are covered."

See [`../common-mistakes/weak-guidance.md`](../common-mistakes/weak-guidance.md) for guideline soup as a failure mode and [`../form-and-style/completion-criteria.md`](../form-and-style/completion-criteria.md) for checkable completion criteria.

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
