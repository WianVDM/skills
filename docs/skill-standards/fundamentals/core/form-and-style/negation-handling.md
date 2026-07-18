# Negation handling

**Layer:** universal fundamentals. **Mode:** rule.

LLMs handle negation weakly. A rule that says "do not X" may still prime the agent toward X. Pair every prohibition with a positive directive.

| Weak | Strong |
|------|--------|
| Do not mock internal functions. | Mock at public seams. Internal functions stay unmocked. |
| Do not write all tests first. | Write one test, then the code to pass it, then repeat. |
| Do not skip the current-state capture. | Run the current-state capture for any ticket with verifiable UI, API, or code state. |

The positive directive tells the agent what *to* do. The negation only clarifies what to avoid.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
