# Iterate

Improve the skill based on test results and real usage.

- Generalize from specific failures rather than overfitting to one prompt.
- Remove instructions that do not change behavior.
- Add scripts when the agent repeatedly generates the same helper code.
- Sharpen completion criteria if the agent rushes.
- Rewrite the description if triggering is unreliable.

See [`../failure-recovery/`](../failure-recovery/) for how to iterate without over-correcting.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
