# Diagnosing ignored skills

**Layer:** universal fundamentals. **Mode:** guide.

When the model loads the skill but does not follow it, start by diagnosing the cause before adding more text. The failure modes themselves are defined in [`../common-mistakes/`](../common-mistakes/); this section focuses on how to diagnose and remediate them.

---

## Diagnosis and remediation guide

| Symptom | Diagnosis | Remediation |
|---|---|---|
| The skill only fires when the user names it explicitly. | Weak description. | Front-load the leading word and add realistic trigger phrases. See [`../../../guides/trigger-evals.md`](../../../guides/trigger-evals.md). |
| The agent misses the key instruction in a wall of text. | Body too long. | Move detail to `references/`; keep the body focused on contract and steps. See [`../structure/`](../structure/). |
| The agent stops when it *feels* done, not when the skill says it is done. | Vague completion criteria. | Rewrite every step to end with a checkable condition. See [`../form-and-style/completion-criteria.md`](../form-and-style/completion-criteria.md). |
| The agent rushes to the visible post-completion steps. | Premature completion. | Sharpen the current step's criterion first; split or delegate the later work if the rush persists. See [`../form-and-style/completion-criteria.md`](../form-and-style/completion-criteria.md). |
| Another rule or context file contradicts the skill. | Conflicting context. | Resolve the conflict in the context file or make the skill's contract more explicit. See [`../../../patterns/context-file.md`](../../../patterns/context-file.md). |
| The agent misses a "do not X" instruction. | Negated rule without a positive directive. | Pair every negative with a positive directive. See [`../form-and-style/negation-handling.md`](../form-and-style/negation-handling.md). |
| A conductor or building block does not invoke the skill. | Skill not reachable by other skills. | Add a reach clause to the description, or make the skill explicitly callable by name. See [`../../../reference/format.md`](../../../reference/format.md). |
| The behavior changed after a harness or model update. | Model drift. | Re-run trigger and behavioral evals; update the description if routing thresholds shifted. |
| The skill reconstructs data from partial sources while a better tool is configured. | Adapter tunnel vision. | Reframe the step around the needed capability, discover available tools, and route through the best one. See [`../common-mistakes/tooling-and-shape-mistakes.md`](../common-mistakes/tooling-and-shape-mistakes.md) and [`../../architecture/tooling-awareness.md`](../../architecture/tooling-awareness.md). |

---

## First-aid checklist

1. Re-run the skill against a small, representative prompt.
2. Check whether the skill loaded at all. If not, rewrite the description.
3. If it loaded, check which steps were followed. If steps were skipped, sharpen completion criteria.
4. If the agent followed the steps but the output is wrong, check for negation, conflicts, and buried rules.
5. Change one variable at a time and re-test.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
