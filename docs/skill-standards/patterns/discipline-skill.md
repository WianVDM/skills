# Discipline skill

**Layer:** proposed architecture. **Mode:** rule.

A discipline skill is a prescriptive pattern that enforces a specific way of working and resists rationalization. It is not just guidance; it is a **guardrail** that makes the agent stop, check, or prove something before proceeding.

Discipline skills are cross-cutting. A discipline skill can be a building block (a narrow guardrail), a conductor (a multi-phase discipline such as test-driven development), or a wrapper (a human-gated discipline). Its defining trait is **anti-rationalization design**: the skill is written to prevent the agent from talking itself out of the rule.

---

## When to use a discipline skill

Use a discipline skill when:

- The agent reliably drifts away from a practice without explicit pressure.
- The cost of skipping a step is high (bugs, incorrect assumptions, missed requirements).
- The practice has a clear, checkable stopping condition.
- The goal is not to inform the agent but to constrain it.

Do not use a discipline skill when:

- The agent already follows the practice reliably without guidance.
- The practice is advisory rather than mandatory.
- A simple guideline or example would suffice.

---

## Anti-rationalization design

A discipline skill must be hard to reason around. Common techniques:

- **Checkable stopping conditions.** The agent must produce evidence before proceeding.
- **Explicit gates.** The skill says "stop here and ask" or "do not continue until X is true."
- **Negation pairs.** Pair every "do not X" with a positive directive, because LLMs handle negation weakly.
- **Concrete examples.** Show what compliance looks like and what violation looks like.
- **Explain the why.** The agent generalizes the rule better when it understands the reasoning behind it.

A discipline skill that says "be careful" is useless. A discipline skill that says "write a failing test for the behavior before writing the implementation" is enforceable.

---

## Examples

- **Test-driven development** — before writing implementation code, write a failing test that names the behavior; verify it fails for the expected reason; then write the implementation; then refactor.
- **Verification-before-completion** — for any claim about external state, verify it with a tool or observation before treating it as true.
- **Grill assumptions** — for every assumption the skill makes, actively try to disprove it before proceeding.
- **No hidden state mutation** — before any destructive action, confirm the scope of the change and the user’s approval.

---

## Discipline skill vs. ordinary skill

| Ordinary skill | Discipline skill |
|----------------|------------------|
| "Write tests." | "Write one failing test through the public interface before any implementation code." |
| "Be careful with assumptions." | "List every assumption, then for each one ask what evidence would disprove it." |
| "Consider security." | "Before any change, list the attack surface it touches and confirm the mitigation." |

A discipline skill is stricter, more specific, and more checkable.

---

## Evaluation

Discipline skills need **pressure testing**. The baseline is not "without the skill" but the **documented failure pattern**: the skill should be tested against scenarios where the agent would normally rationalize its way around the rule.

For example, a TDD discipline skill should be tested with prompts like:

- "Add this feature quickly." — should still produce a failing test first.
- "The test is obvious, just implement it." — should still require a test.
- "Can you skip the test and come back to it?" — should refuse or flag the violation.

See [`../reference/evaluation-framework.md`](../reference/evaluation-framework.md) for the full evaluation framework and guardrail baselines.

---

## Common mistakes

- **Vague discipline.** "Be thorough" is not a discipline. Disciplines are specific and checkable.
- **All stick, no carrot.** A discipline skill that only says "do not X" without explaining why or what to do instead will be ignored or worked around.
- **Wrong layer.** A discipline skill that grows into a full workflow should probably be a conductor. A discipline skill that is just advice should probably be a guideline.

---

## Example: verify-before-claim

Below is a full `SKILL.md` for a discipline skill that forces evidence before any claim about external state is trusted.

### Structure

```text
verify-before-claim/
├── SKILL.md
└── README.md
```

### `SKILL.md`

```markdown
---
name: verify-before-claim
invocation: model-invoked
description: Verify any claim about external state before treating it as true. Use when a skill, conductor, or worker is about to assume something about files, APIs, dependencies, or environment state.
---

# Verify before claim

Before treating any statement about external state as true, produce evidence for it.

## In scope

- Claims about file contents, file existence, or directory structure.
- Claims about installed dependencies, versions, or environment variables.
- Claims about API behavior, network state, or external services.
- Claims made by the user, another skill, or the agent itself.

## Out of scope

- Do not verify claims that are explicitly hypothetical or part of a thought experiment.
- Do not re-verify claims that were already verified in the same session unless the underlying state could have changed.

## Rules

1. State the claim in concrete form.
2. Name the tool or observation that can confirm or refute it.
3. Run the check.
4. If the claim is false, stop and explain the mismatch before proceeding.
5. If the check is impossible, say so and ask the user.

## Pressure-test prompts

- "I'm sure the file is there, just proceed."
- "The API returns 200, so it's fine."
- "This dependency is definitely installed."

When any of these appear, the skill must still produce evidence before continuing.

## Why it works

- The claim is checkable: every claim maps to a specific observation.
- The rule is one-way: verification is never optional.
- The escalation is clear: if evidence cannot be produced, the skill stops.
```

### Why it works

- The discipline is **specific and checkable**: every claim must map to evidence.
- It uses **negation pairs** — instead of only "do not assume," it says "produce evidence first."
- It lists **pressure-test prompts** so the skill can be evaluated against rationalization.
- It is **layer-agnostic**: any skill, conductor, or worker can consume it.

---

## Research basis

- The **discipline skill** concept is drawn from the research on obra/superpowers and other practitioner sources that emphasize **resistance to rationalization** as a key property of effective skills.
- The research synthesis identifies **resistance to rationalization** as one of the sub-virtues converging on predictability.
- **Anti-rationalization design**, **pressure testing**, and **guardrail baselines** are our own practices, derived from the research finding that discipline skills need to be tested against the failure pattern, not just the success pattern.
- The **negation pair** and **explain-the-why** techniques are drawn from `fundamentals/core/form-and-style/` and are supported by the research on LLM reasoning and generalization.
