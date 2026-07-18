# Detecting failures

**Layer:** universal fundamentals. **Mode:** guide.

Failures come in two shapes. Loud failures are easy to spot. Silent failures are common and dangerous.

---

## Loud failures

A loud failure is easy to spot because something breaks visibly:

- The agent refuses to run the skill or reports that it cannot find it.
- A required tool or capability is missing and the skill fails closed.
- The output is clearly wrong: wrong file format, wrong language, wrong scope.
- The agent produces an error or hallucinates a tool call.

Loud failures are usually caused by missing dependencies, broken references, incorrect frontmatter, or a mismatch between the skill's declared scope and the user's request.

---

## Silent failures

Silent failures are more common and more dangerous. The agent appears to work, but the skill is not doing its job:

| Symptom | What is probably happening |
|---|---|
| The skill never loads for relevant queries. | The `description` is too weak or too narrow. |
| The skill loads but the agent ignores its steps. | The body is too long, vague, or crowded by conflicting context. |
| The agent starts the right process but skips the end. | Completion criteria are unclear or post-completion steps pull attention forward. |
| The output looks right but violates a rule. | The rule is stated as a negation or buried in detail. |
| The skill fires for unrelated queries. | The `description` is too broad or shares keywords with another skill. |
| The agent re-derives behavior the skill already encodes. | The skill is not being reached by the model, or the contract is not load-bearing. |
| The skill reconstructs data from partial sources while a better tool is configured. | **Adapter tunnel vision**: the skill treats its own adapters as the only way to fulfill a capability. See [`../common-mistakes/tooling-and-shape-mistakes.md`](../common-mistakes/tooling-and-shape-mistakes.md) and [`../../architecture/tooling-awareness.md`](../../architecture/tooling-awareness.md). |

---

## Signals to watch

To detect silent failures early, watch for:

- **Trace and tool calls.** Did the agent read the files the skill told it to read? Did it run the expected commands?
- **Output shape.** Does the output match the contract the skill defines? (Format, scope, depth, style.)
- **Completion criteria.** Did the agent stop at the checkable condition defined in the skill, or did it stop early?
- **Trigger coverage.** Do representative user prompts actually load the skill? (See [`../../../guides/trigger-evals.md`](../../../guides/trigger-evals.md).)
- **Comparison.** Run the same task with and without the skill. If the output is the same, the skill is not changing behavior.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
