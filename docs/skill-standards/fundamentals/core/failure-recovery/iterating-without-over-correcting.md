# Iterating without over-correcting

**Layer:** universal fundamentals. **Mode:** rule.

The natural reaction to a failing skill is to add more instructions. That usually makes the skill longer, noisier, and less reliable. Iterate with discipline instead.

---

## Change one variable at a time

- Rewrite the `description`, *or* tighten a completion criterion, *or* move a reference out of the body. Do not do all three at once.
- After each change, run the same eval set to see what moved.
- If a change does not improve behavior, revert it rather than layering on more text.

---

## Distinguish skill failure from harness or model failure

- If the skill never loads despite a strong description, the harness routing may have changed.
- If the skill loads but the model ignores a clear instruction, the model may be struggling with the phrasing or context budget.
- If the skill works in one harness but not another, check portability and degradation behavior. See [`../../../patterns/portability.md`](../../../patterns/portability.md).

Do not rewrite the skill to compensate for transient harness behavior unless the behavior is stable and reproducible.

---

## Prefer removal over addition

- Before adding a new rule, ask: *will this change behavior versus the default?* If not, it is a no-op instruction.
- Before adding a synonym to the description, ask: *is this a distinct branch or just another way to say the same thing?* If it is the same branch, it adds noise.
- Before adding a new step, ask: *can I sharpen the existing step instead?*

---

## Keep a failure log

For skills that iterate often, keep a `references/FAILURES.md` or `references/ITERATIONS.md` file:

- What failed.
- What was tried.
- What worked.
- What was reverted and why.

This prevents the same over-correction from being reintroduced and makes the skill's evolution auditable.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
