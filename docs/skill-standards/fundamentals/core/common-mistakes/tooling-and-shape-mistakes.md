# Tooling and shape mistakes

**Layer:** universal fundamentals. **Mode:** rule.

Tooling and shape mistakes are the class of mistakes where the skill uses the wrong tool or the wrong abstraction. The skill either reaches for its own built-in adapters when better tools are available, or it is forced into a shape that does not match the problem.

---

## Adapter tunnel vision

The skill treats its own built-in adapters, scripts, or preferred paths as the only way to fulfill a capability, ignoring better tools that are already configured or available.

See [`../../architecture/tooling-awareness.md`](../../architecture/tooling-awareness.md) for the capability-first approach to tool selection and [`../failure-recovery/diagnosing-ignored-skills.md`](../failure-recovery/diagnosing-ignored-skills.md) for diagnosing this symptom in failure recovery.

---

## Wrong type for the job

Forcing a skill into a shape that does not match the problem.

**Examples**

- A conductor skill that does all the work inline.
- A building block that tries to coordinate other skills.
- A building-block skill that includes a workflow.

**Cure**

Revisit [`../types/`](../../architecture/types/). Choose the type that matches the work.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
