# Failure recovery and iteration

**Layer:** universal fundamentals. **Mode:** reference.

A skill failure is not always a stack trace. Most failures are silent: the agent does not load the skill, loads it but ignores the contract, or follows the steps in a way that looks correct but misses the intent.

Read this if a skill is not firing, is being ignored, is producing inconsistent output, or has grown too large to maintain.

---

## Deeper topics

- [`detecting-failures.md`](./detecting-failures.md) — silent vs. loud failures and the signals to watch.
- [`diagnosing-ignored-skills.md`](./diagnosing-ignored-skills.md) — a symptom-diagnosis-remediation guide for skills the model loads but does not follow.
- [`iterating-without-over-correcting.md`](./iterating-without-over-correcting.md) — change one variable, distinguish skill failure from harness failure, prefer removal, and keep a failure log.
- [`split-prune-retire.md`](./split-prune-retire.md) — when to split, prune, or retire a skill.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
