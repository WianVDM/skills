# One-way pattern consistency

A reusable skill should encode exactly one canonical way to solve each recurring problem. When a skill offers multiple valid approaches, the agent faces decision paralysis and output becomes inconsistent.

| Inconsistent skill | Consistent skill |
|--------------------|------------------|
| "Use either classes or factory functions." | "Use factory functions for create-X helpers." |
| "Return errors or throw, whichever you prefer." | "Throw for programmer errors; return `Result` for expected failures." |
| "Use mocks or stubs as needed." | "Use stubs for dependencies; avoid mocking internal functions." |

One-way consistency does not mean ignoring context. It means the skill makes the default choice explicit and explains when to deviate.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
