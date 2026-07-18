# Explain the why

**Layer:** universal fundamentals. **Mode:** rule.

A skill should explain the reasoning behind its guidance, not just issue commands. Today's models have strong theory of mind and generalize better when they understand intent. This applies to steps and phases too: a one-line rationale for why a phase exists ("why this step before the next") reduces premature completion and helps the agent judge how much legwork is required.

| Rigid command | Explain-the-why |
|---------------|-----------------|
| NEVER mock internal functions. | Mocking internal functions couples tests to implementation. Prefer mocking at seams where the implementation can change without breaking the test. |
| ALWAYS write one test per behavior. | One test per behavior keeps failures diagnostic: a failing test points to one capability, not many. |

If you find yourself writing `ALWAYS`, `NEVER`, or `MUST` in all caps, treat it as a yellow flag. Reframe the instruction by explaining why the rule exists. The agent will apply it more reliably and adapt it better to edge cases.

Exceptions remain valid. Some safety or compliance rules are absolute. Mark those explicitly and explain why no exception is allowed.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
