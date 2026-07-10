# Skill vs script

A script is deterministic: same input, same output, no reasoning. A skill is judgment-shaped: it guides how the agent reasons.

| Use a script | Use a skill |
|--------------|-------------|
| Detect the project's package manager. | Decide which verification method fits a ticket. |
| Parse a ticket key from a branch name. | Investigate and synthesize ticket context. |
| Run the test suite and return results. | Decide whether the test suite's failure is blocking. |

A skill may call scripts. A script should not call a skill.

---

## Scripts-first rule

When designing a skill, default to scripts for any logic that is deterministic, repeatable, and stable. Only keep logic in `SKILL.md` when it requires judgment, context, or adaptation.

Signs that a script should exist:

- The agent repeatedly generates the same helper code across invocations.
- The operation has clear inputs and outputs.
- The operation can be tested independently.
- The logic is stable enough that regenerating it each time wastes tokens.

Scripts live in `scripts/`, are referenced from `SKILL.md`, and execute without loading their source into context. This is cheaper and more reliable than asking the agent to recreate the logic each time.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
