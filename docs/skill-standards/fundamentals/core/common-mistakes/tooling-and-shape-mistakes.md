# Tooling and shape mistakes

Tooling and shape mistakes are the class of mistakes where the skill uses the wrong tool or the wrong abstraction. The skill either reaches for its own built-in adapters when better tools are available, or it is forced into a shape that does not match the problem.

---

## Adapter tunnel vision

The skill treats its own built-in adapters, scripts, or preferred paths as the only way to fulfill a capability, ignoring better tools that are already configured or available.

**Symptoms**

- Reconstructing data from partial outputs instead of using a better tool.
- Declaring a source "unavailable" when an MCP server or native tool could reach it.
- Recording limitations and moving on without suggesting alternatives.
- Marking a section complete while a better tool sits unused.

**Cure**

Design each capability step as "what outcome do I need?" first, then "which available tool gives the best result?" Route through the best tool and disclose the choice.

See [`../../architecture/tooling-awareness.md`](../../architecture/tooling-awareness.md) for the capability-first alternative and [`../failure-recovery/diagnosing-ignored-skills.md`](../failure-recovery/diagnosing-ignored-skills.md) for the adapter tunnel vision symptom in failure recovery.

---

## Wrong type for the job

Forcing a skill into a shape that does not match the problem.

**Examples**

- A conductor skill that does all the work inline.
- A building block that tries to coordinate other skills.
- A building-block skill that includes a workflow.

**Cure**

Revisit [`../types/`](../types/). Choose the type that matches the work.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
