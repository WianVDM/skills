# Building block

**Layer:** proposed architecture. **Mode:** rule.

A building block is a narrow skill that does one thing well and has a clear interface. It is the primary unit of reuse in the library.

A building block can be invoked by a human, by another skill, or by a conductor. Its defining trait is focus, not its consumer.

---

## When to use

- The task is well-bounded.
- The skill provides a capability that could be reused by conductors or other skills.
- The output should be structured and predictable.

---

## Examples

- `find-skills` — discovers available skills and returns structured results.
- `install-skill` — installs a skill given a name or source.
- `verify-skill` — checks a skill against the standards.
- `summarize-text` — compacts text into a specified format.

---

## When to extract one

A capability should become a separate building block only when extraction is justified by reuse — not because it is self-contained or might be useful later. See [`../../../patterns/building-block.md`](../../../patterns/building-block.md) for the extraction criteria and the colocation rule.

## Characteristics

- Usually **model-invoked** if other skills or conductors need to reach it.
- Can be **user-invoked** if only humans use it directly.
- Small, focused `SKILL.md` with a clear contract.
- Declares dependencies explicitly.
- Produces structured output that consumers can act on.
- Avoids presentation, workflow, or coordination concerns.

---

## Common mistake

Adding presentation logic, workflow phases, or heavy state management that belongs in a wrapper or conductor. A building block should stay narrow.

See [tooling and shape mistakes][tooling-mistakes] for wrong type for the job.

---

## Research basis

See [sources.md][sources].

[sources]: ../../../reference/sources.md
[tooling-mistakes]: ../../core/common-mistakes/tooling-and-shape-mistakes.md
