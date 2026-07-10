# Weak guidance

Weak guidance is the class of mistakes that say something without giving the agent enough purchase to act. The result is either no change in behavior or behavior that varies unpredictably.

---

## No-op instructions

A line that changes nothing because the model already does it by default. Common examples include "be thorough" or "think carefully." The agent is already doing those things, so the instruction is a no-op.

**Cure**

Run the no-op test on every line: *does this change behavior versus the default?* If not, delete it or replace it with a stronger leading word or a checkable completion criterion.

See [`../form-and-style/pruning.md`](../form-and-style/pruning.md) for the no-op test and [`../form-and-style/leading-words.md`](../form-and-style/leading-words.md) for how to use leading words instead.

---

## Vague completion criteria

A step ends with fuzzy language like "understand the problem" or "produce a plan." Vague criteria invite premature completion: the agent declares the step done because the criterion is impossible to falsify.

See [`../form-and-style/completion-criteria.md`](../form-and-style/completion-criteria.md) for how to write strong, checkable completion criteria.

---

## Over-reliance on priors

Assuming the agent already knows what you mean. This works for well-known tasks and fails for domain-specific or ambiguous ones.

**Examples**

- "Write a summary document" — the agent probably knows the shape.
- "Follow clean architecture" — the agent's version may not match yours.
- "Be pragmatic" — too vague; every agent has a different prior.

**Cure**

Use leading words where priors are strong. Define terms where they are domain-specific. Add steps where the agent would vary.

See [`../form-and-style/leading-words.md`](../form-and-style/leading-words.md) for how to use priors deliberately.

---

## Guideline soup

A skill that says many true things but gives the agent no purchase point. Often caused by weak or missing leading words and completion criteria.

**Example**

> Bad: "Be thorough. Consider edge cases. Write good tests."
>
> Better: "For each public behavior, write one test through the public interface. Stop when the user confirms the listed behaviors are covered."

**Cure**

Turn vague guidance into specific principles, leading words, or checkable criteria. See [`../form-and-style/anti-patterns.md`](../form-and-style/anti-patterns.md) for the full guideline-soup anti-pattern.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
