# Wrapper

A wrapper skill is a thin layer that adapts a building block or conductor for human interaction. It adds prompts, presentation, confirmation, and user-facing language.

---

## When to use

- A building block or conductor exists but needs user-facing prompts or confirmation.
- The user should see a curated summary rather than raw output.
- The workflow needs explicit human gates between phases.

---

## Examples

- A find-and-install concierge that uses `find-skills` and `install-skill`.
- A report viewer that presents a `debrief` report in a concise format.
- A confirmation gate before a destructive building block runs.

---

## Characteristics

- Usually **user-invoked** because its primary consumer is the human. May be model-invoked only when the harness explicitly supports it and the use case requires autonomous routing.
- Thin: no core logic that belongs in the wrapped skill.
- Focused on prompts, presentation, and confirmation.
- May act as a router, naming several related skills and when to reach for each.

---

## Common mistake

Letting the wrapper grow into a conductor by adding phases, state, or complex coordination. If that happens, promote it to a conductor.

See [`../common-mistakes/tooling-and-shape-mistakes.md`](../common-mistakes/tooling-and-shape-mistakes.md) for wrong type for the job and [`../../../patterns/wrapper.md`](../../../patterns/wrapper.md) for the full wrapper pattern.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
