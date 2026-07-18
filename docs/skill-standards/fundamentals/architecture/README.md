# Architecture fundamentals

**Layer:** proposed architecture. **Mode:** reference.

Opt-in rules for skills that participate in the architecture: shared, composed, distributed, portable, or otherwise consumed by other skills.

---

## Topics

- [`types/`](./types/) — building block, conductor, wrapper, and multi-layer/hybrid skills; choosing and migrating types.
- [`tooling-awareness.md`](./tooling-awareness.md) — capability-first tool selection, discovery, and degradation disclosure.
- [`standards-path.md`](./standards-path.md) — resolving canonical skill-standards paths without hardcoding project conventions.
- [`security.md`](./security.md) — secrets, destructive actions, external access, and fail-closed behavior.
- [`dependencies-and-bundling.md`](./dependencies-and-bundling.md) — dependency taxonomy, declaration surfaces, lazy evaluation, and self-diagnostics.
- [`evaluation.md`](./evaluation.md) — eval-driven development, trigger/behavior/composition/pressure tests, and review questions.
- [`mode.md`](./mode.md) — what a mode is, why it is not a skill, and why skills must not depend on modes.

---

## Where architecture fits in

See [`../README.md`](../README.md) for how architecture fundamentals relate to core fundamentals, patterns, guides, and reference material.

---

## Reading order

If your skill will be shared, consumed by conductors, or run across projects or harnesses, read these topics in order:

1. [`types/`](./types/)
2. [`tooling-awareness.md`](./tooling-awareness.md)
3. [`standards-path.md`](./standards-path.md)
4. [`security.md`](./security.md)
5. [`dependencies-and-bundling.md`](./dependencies-and-bundling.md)
6. [`evaluation.md`](./evaluation.md)
