# Context Budget and Performance

**Layer:** universal fundamentals. **Mode:** rule.

Model-invoked skills live in the agent's context window. Every such skill pays **context load** on every turn: its description, and sometimes key excerpts from its body, compete for limited space and attention. This document gives practical guidance for keeping that cost low while keeping skills useful.

---

## What context load costs

A model-invoked skill consumes context in two ways:

1. **Description load** — the `description` is held in context for routing. This is unavoidable for model-invoked skills.
2. **Body load** — some harnesses or retrieval mechanisms also pull in parts of the `SKILL.md` body when the skill is selected. A long body increases the cost of each invocation.

User-invoked skills pay **cognitive load** instead: the user must remember they exist. They pay no per-turn description load. Choose user-invoked for skills that rarely need to fire autonomously.

---

## Description length

Aim for **under 1024 characters** for every model-invoked description. Some harnesses impose shorter limits or penalize long descriptions in routing quality. For the full description craft guidance — leading words, distinct triggers, and reach clauses — see [`FORMAT.md`](../../reference/format.md).

---

## When to split a skill

Splitting a skill creates a new model-invoked description and therefore new context load. Split only when the new description earns its place: a distinct leading word, a consumer that must reach the skill by name, or a branch long enough to hide its post-completion steps. Do not split for organization alone.

See [`../architecture/types/choosing-a-type.md`](../architecture/types/choosing-a-type.md) for the splitting rule and [`./failure-recovery/split-prune-retire.md`](./failure-recovery/split-prune-retire.md) for the operational side.

---

## When to merge skills

Merge skills when:

- They compete for the same keywords and cause false positives.
- One skill is just a thin wrapper around the other.
- Their descriptions are so similar that the model cannot reliably distinguish them.

Merged skills can still use branches or references to keep the top-level clean. See `fundamentals/core/common-mistakes/` for duplication and bloat guidance.

---

## Managing many model-invoked skills

A large library of model-invoked skills can crowd the context window. Strategies:

### 1. Make rarely-used skills user-invoked

If a skill only fires when the user explicitly asks, make it user-invoked. The cost shifts from context to human memory. A **router skill** — one user-invoked skill that names the others and when to reach for each — reduces that memory load. See [`../../patterns/wrapper.md`](../../patterns/wrapper.md) for the router pattern.

### 2. Use namespacing and packages

Namespacing (`package-name:skill-name`) lets harnesses load only the skills from a relevant package. Declare packages in `skills.json` and use namespaces to avoid collisions without inflating the top-level routing surface.

### 3. Prefer building blocks and conductors

A few well-composed conductors and building blocks can replace many overlapping skills. A conductor delegates to building blocks; only the conductor's description needs to stay in context for routing.

### 4. Progressive disclosure

Keep the `SKILL.md` body short. Move edge cases, schemas, examples, and deep reference into `references/`. The body is loaded only when the skill is selected; the description is loaded on every turn. Do not let a long body become a per-turn cost.

---

## Context-compaction survival

Long sessions are summarized or truncated by the harness. Skills that must survive across compaction should:

- Write state to files in `.agents/context/{skill-name}/` rather than relying on in-context memory.
- Produce context reports that other skills can resume from.
- Keep their own ledgers or logs so the next invocation can reconstruct progress.

See `patterns/stateful.md` and `patterns/context-reports.md` for the stateful and report patterns.

---

## Practical rules of thumb

- **Keep model-invoked descriptions under 1024 characters.**
- **Front-load the leading word.** The first 10–15 words matter most.
- **Use user-invoked for skills that fire less than once per few sessions.**
- **Limit active model-invoked skills to the ones that must fire autonomously.** The rest can be user-invoked or consumed by conductors.
- **Split only when a new description earns its place.** If the new skill is not independently triggered, keep it as a reference or sub-step.
- **Move detail out of `SKILL.md`.** `references/` is for detail; the body is for the contract.

---

## Example: trimming a description

Before:

```yaml
description: This skill is a helpful utility that assists users with the task of reviewing their UI code in order to check for any potential accessibility issues and design-system violations that may exist.
```

After:

```yaml
description: Review UI code for accessibility and design-system compliance. Use when asked to "review my UI", "check accessibility", or "audit design".
```

The trimmed version drops the throat-clearing ("This skill is a helpful utility"), names the domain in the first three words, and replaces vague scope ("any potential issues") with triggers the router can match. See [`../../reference/format.md`](../../reference/format.md) for the description craft rules and [`../../guides/trigger-evals.md`](../../guides/trigger-evals.md) for how to test the result.

---

## Limitations

- **Exact harness limits** (context window size, description budget, routing tokenization) vary and are often proprietary. Treat the 1024-character target as a safe heuristic, not a universal constant.
- **Trigger thresholds** are not published by any harness, so empirical testing is the only reliable way to know whether a description fires correctly.
- **Body loading behavior** differs: some harnesses load the whole body, some only load sections, some retrieve on demand. Keep the body lean as a defensive default.

---

## Related documents

- [`../architecture/types/`](../architecture/types/) — choosing invocation mode and splitting rules.
- [`common-mistakes/`](./common-mistakes/) — bloat, duplication, and premature completion.
- [`structure/`](./structure/) — progressive disclosure and the information hierarchy.
- [`format.md`](../../reference/format.md) — the `description` field and frontmatter schema.
- [`patterns/building-block.md`](../../patterns/building-block.md) — narrow, reusable skills that reduce duplication.
- [`patterns/conductor.md`](../../patterns/conductor.md) — composing skills without multiplying descriptions.
- [`patterns/wrapper.md`](../../patterns/wrapper.md) — user-invoked adaptation layer.
- [`patterns/stateful.md`](../../patterns/stateful.md) — surviving context compaction.
- [`patterns/context-reports.md`](../../patterns/context-reports.md) — resumable structured outputs.

---

## Research basis

- Context load and description-budget framing, from the [Claude Code skills documentation](https://code.claude.com/docs/en/skills) and the context-stack analysis across harnesses, consolidated in [`../../reference/sources.md`](../../reference/sources.md).
- The 1024-character target and the "first 10–15 words" heuristic: original to this repo. Exact harness limits and trigger thresholds are proprietary, so these are safe heuristics, not universal constants (see Limitations).
