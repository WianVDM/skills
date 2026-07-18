# Leading words and priors

**Layer:** universal fundamentals. **Mode:** rule.

A **leading word** is a compact concept already present in the model's pretraining. Using it anchors behavior in fewer tokens.

| Instead of | Leading word |
|------------|--------------|
| fast, deterministic, low-overhead | tight |
| a loop you believe in | red |
| interview relentlessly until nothing is unclear | grill |
| hide complexity behind a simple interface | deep |

Leading words work because they recruit priors the model already holds. They improve predictability while keeping the skill short.

A leading word must be reinforced by context. If the skill uses `deep`, it must define what deep means in this domain at least once, then rely on the word thereafter.

A leading word can also anchor **invocation**: when the same word appears in the user's prompts, docs, and codebase, the agent links that shared language to the skill and fires it more reliably. Front-load the leading word in the skill's description.

A weak leading word that does not beat the default is a **no-op**. The fix is a stronger word, not a different technique.

See [`../common-mistakes/weak-guidance.md`](../common-mistakes/weak-guidance.md) for over-reliance on priors as a failure mode and [`./pruning.md`](./pruning.md) for the no-op test.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
