# Workflow mistakes

Workflow mistakes are the class of mistakes that make the agent follow the skill mechanically or rush through it. The skill is either too prescriptive about mechanics or too easy to complete early.

---

## Manual in disguise

A skill that lists every keystroke and command. The agent becomes a slow script executor.

**Example**

> Bad: "Run `git status`, then `git diff`, then `git log --oneline -5`."
>
> Better: "Understand the current working state before making changes."

**Cure**

State intent, not mechanics. Use scripts for deterministic steps that must be repeated exactly.

See [`../form-and-style/anti-patterns.md`](../form-and-style/anti-patterns.md) for the full manual-in-disguise anti-pattern.

---

## Premature completion

Ending a step before it is genuinely done because the agent's attention slips toward being finished.

**Cure**

Sharpen the completion criterion first. Only if the criterion is irreducibly fuzzy and you actually observe the rush should you hide the later steps by splitting the skill.

See [`../form-and-style/completion-criteria.md`](../form-and-style/completion-criteria.md) for how completion criteria and post-completion steps cause or prevent this.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
