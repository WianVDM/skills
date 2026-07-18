# Design

**Layer:** universal fundamentals. **Mode:** guide.

Choose the skill type and form before writing files.

- **Type**: building block, conductor, wrapper, or multi-layer. See [`../types/`](../../architecture/types/).
- **Form**: instruction-heavy, guideline-heavy, or hybrid. See [`../form-and-style/`](../form-and-style/).
- **Invocation**: model-invoked or user-invoked. See [`../structure/frontmatter.md`](../structure/frontmatter.md).
- **Scope**: what is in and what is out.
- **Dependencies**: other skills, tools, APIs, environment variables. Decide which are required, recommended, or optional, and whether recommended/optional dependencies should be evaluated lazily when the relevant method or branch is selected.

Write a one-sentence intent statement:

> This skill makes the agent more predictable at ______ by enforcing ______.

If both blanks are hard to fill, the design is not ready.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
