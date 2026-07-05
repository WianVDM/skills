# Failure Recovery and Iteration

## At a glance

A skill failure is not always a stack trace. Most failures are silent: the agent does not load the skill, loads it but ignores the contract, or follows the steps in a way that looks correct but misses the intent. This document covers how to detect both silent and loud failures, diagnose the root cause, iterate without over-correcting, and decide when to split, prune, or retire a skill.

**Read this if:** a skill is not firing, is being ignored, is producing inconsistent output, or has grown too large to maintain.

---

## Detecting silent vs. loud failures

### Loud failures

A loud failure is easy to spot because something breaks visibly:

- The agent refuses to run the skill or reports that it cannot find it.
- A required tool or capability is missing and the skill fails closed.
- The output is clearly wrong: wrong file format, wrong language, wrong scope.
- The agent produces an error or hallucinates a tool call.

Loud failures are usually caused by missing dependencies, broken references, incorrect frontmatter, or a mismatch between the skill's declared scope and the user's request.

### Silent failures

Silent failures are more common and more dangerous. The agent appears to work, but the skill is not doing its job:

| Symptom | What is probably happening |
|---|---|
| The skill never loads for relevant queries. | The `description` is too weak or too narrow. |
| The skill loads but the agent ignores its steps. | The body is too long, vague, or crowded by conflicting context. |
| The agent starts the right process but skips the end. | Completion criteria are unclear or post-completion steps pull attention forward. |
| The output looks right but violates a rule. | The rule is stated as a negation or buried in detail. |
| The skill fires for unrelated queries. | The `description` is too broad or shares keywords with another skill. |
| The agent re-derives behavior the skill already encodes. | The skill is not being reached by the model, or the contract is not load-bearing. |

### Signals to watch

To detect silent failures early, watch for:

- **Trace and tool calls.** Did the agent read the files the skill told it to read? Did it run the expected commands?
- **Output shape.** Does the output match the contract the skill defines? (Format, scope, depth, style.)
- **Completion criteria.** Did the agent stop at the checkable condition defined in the skill, or did it stop early?
- **Trigger coverage.** Do representative user prompts actually load the skill? (See [`TRIGGER_EVALS.md`](../TRIGGER_EVALS.md).)
- **Comparison.** Run the same task with and without the skill. If the output is the same, the skill is not changing behavior.

---

## What to do when the model ignores the skill

When the model loads the skill but does not follow it, start by diagnosing the cause before adding more text.

### Common causes and fixes

| Cause | Diagnosis | Fix |
|---|---|---|
| **Weak description** | The skill only fires when the user names it explicitly. | Front-load the leading word and add realistic trigger phrases. See [`TRIGGER_EVALS.md`](../TRIGGER_EVALS.md). |
| **Body too long** | The agent misses the key instruction in a wall of text. | Move detail to `references/`; keep the body focused on contract and steps. See [`structure.md`](./structure.md). |
| **Vague completion criteria** | The agent stops when it *feels* done, not when the skill says it is done. | Rewrite every step to end with a checkable condition. See [`form-and-style.md`](./form-and-style.md). |
| **Premature completion** | The agent rushes to the visible post-completion steps. | Sharpen the current step's criterion first; split or delegate the later work if the rush persists. See [`form-and-style.md`](./form-and-style.md). |
| **Conflicting context** | Another rule or context file contradicts the skill. | Resolve the conflict in the context file or make the skill's contract more explicit. See [`context-file.md`](../patterns/context-file.md). |
| **Negated rules** | The agent misses a "do not X" instruction. | Pair every negative with a positive directive. See [`form-and-style.md`](./form-and-style.md). |
| **Skill not reached by other skills** | A conductor or building block does not invoke the skill. | Add a reach clause to the description, or make the skill explicitly callable by name. See [`FORMAT.md`](../FORMAT.md). |
| **Model drift** | The behavior changed after a harness or model update. | Re-run trigger and behavioral evals; update the description if routing thresholds shifted. |

### First-aid checklist

1. Re-run the skill against a small, representative prompt.
2. Check whether the skill loaded at all. If not, rewrite the description.
3. If it loaded, check which steps were followed. If steps were skipped, sharpen completion criteria.
4. If the agent followed the steps but the output is wrong, check for negation, conflicts, and buried rules.
5. Change one variable at a time and re-test.

---

## How to iterate without over-correcting

The natural reaction to a failing skill is to add more instructions. That usually makes the skill longer, noisier, and less reliable. Iterate with discipline instead.

### Change one variable at a time

- Rewrite the `description`, *or* tighten a completion criterion, *or* move a reference out of the body. Do not do all three at once.
- After each change, run the same eval set to see what moved.
- If a change does not improve behavior, revert it rather than layering on more text.

### Distinguish skill failure from harness or model failure

- If the skill never loads despite a strong description, the harness routing may have changed.
- If the skill loads but the model ignores a clear instruction, the model may be struggling with the phrasing or context budget.
- If the skill works in one harness but not another, check portability and degradation behavior. See [`PORTABILITY.md`](../../PORTABILITY.md).

Do not rewrite the skill to compensate for transient harness behavior unless the behavior is stable and reproducible.

### Prefer removal over addition

- Before adding a new rule, ask: *will this change behavior versus the default?* If not, it is a no-op instruction.
- Before adding a synonym to the description, ask: *is this a distinct branch or just another way to say the same thing?* If it is the same branch, it adds noise.
- Before adding a new step, ask: *can I sharpen the existing step instead?*

### Keep a failure log

For skills that iterate often, keep a `references/FAILURES.md` or `references/ITERATIONS.md` file:

- What failed.
- What was tried.
- What worked.
- What was reverted and why.

This prevents the same over-correction from being reintroduced and makes the skill's evolution auditable.

---

## When to split, prune, or retire a skill

### Split a skill

Splitting is the right move when a branch of the skill has become a distinct responsibility. Split when:

- The branch has a **distinct leading word** that should trigger it on its own.
- Another skill or conductor **must reach it by name**.
- The branch is **long and independent** enough that hiding its post-completion steps improves the parent skill.
- The description is becoming too broad because it must cover two very different tasks.

Do not split just for organization. If the split skill would rarely be used on its own, keep it as a reference or sub-step. See [`CONTEXT_BUDGET.md`](../CONTEXT_BUDGET.md) for splitting guidance.

### Prune a skill

Prune when the skill has accumulated sediment. Remove:

- Lines that do not change behavior versus the default.
- Duplicate or near-duplicate guidance.
- Stale examples or framework-specific advice that no longer applies.
- Instructions that are too specific to one project or harness.
- Branches the skill no longer handles.

After pruning, re-run the eval set. If the skill still passes, the removed material was sediment. See [`common-mistakes.md`](./common-mistakes.md).

### Retire a skill

Retire a skill when it is no longer the best solution:

- It is no longer used.
- Its job is better handled by a script, an MCP server, or another skill.
- It has grown too many unrelated concerns and splitting would not help.
- A newer version or a different skill replaces it.

When retiring:

1. Mark the skill as deprecated in `SKILL.md` and `skills.json`.
2. Document the replacement path.
3. Update skills that depended on it.
4. After a reasonable transition period, remove the skill directory or move it to an archive.

See [`MIGRATION.md`](../MIGRATION.md) and [`fundamentals/lifecycle.md`](./lifecycle.md).

---

## Key takeaways

- Watch for **silent failures** (ignored, bypassed, or misapplied skills) as much as loud failures.
- The first fix for an ignored skill is usually to **sharpen the description or completion criteria**, not to add more instructions.
- **Iterate one variable at a time** and measure with evals before making the next change.
- **Distinguish skill failure from harness or model failure**; do not rewrite the skill to compensate for transient behavior.
- **Split** when a branch has a distinct leading word or must be reached by another skill.
- **Prune** when the skill has accumulated sediment, duplication, or no-op instructions.
- **Retire** when the skill is unused, replaced, or too fractured to maintain.

---

## Related documents

- [`TRIGGER_EVALS.md`](../TRIGGER_EVALS.md) — testing whether a skill fires at the right times.
- [`EVALUATION.md`](../EVALUATION.md) — the full evaluation framework.
- [`CONTEXT_BUDGET.md`](../CONTEXT_BUDGET.md) — when to split or merge skills for context efficiency.
- [`fundamentals/form-and-style.md`](./form-and-style.md) — completion criteria, leading words, and negation pairs.
- [`fundamentals/common-mistakes.md`](./common-mistakes.md) — bloat, sediment, duplication, and no-op instructions.
- [`fundamentals/structure.md`](./structure.md) — progressive disclosure and the information hierarchy.
- [`fundamentals/lifecycle.md`](./lifecycle.md) — draft, test, publish, maintain, retire.
- [`MIGRATION.md`](../MIGRATION.md) — shape changes and deprecation paths.
- [`PORTABILITY.md`](../../PORTABILITY.md) — degradation and cross-harness behavior.
