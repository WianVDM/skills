# Split, prune, or retire

Not every failing skill can be saved. Sometimes the right move is to split it, prune it, or remove it.

---

## Split a skill

Splitting is the right move when a branch of the skill has become a distinct responsibility. Split when:

- The branch has a **distinct leading word** that should trigger it on its own.
- Another skill or conductor **must reach it by name**.
- The branch is **long and independent** enough that hiding its post-completion steps improves the parent skill.
- The description is becoming too broad because it must cover two very different tasks.

Do not split just for organization. If the split skill would rarely be used on its own, keep it as a reference or sub-step. See [`../../../reference/context-budget.md`](../../../reference/context-budget.md) for splitting guidance.

---

## Prune a skill

Prune when the skill has accumulated sediment. Remove:

- Lines that do not change behavior versus the default.
- Duplicate or near-duplicate guidance.
- Stale examples or framework-specific advice that no longer applies.
- Instructions that are too specific to one project or harness.
- Branches the skill no longer handles.

After pruning, re-run the eval set. If the skill still passes, the removed material was sediment. See [`../common-mistakes/bloat.md`](../common-mistakes/bloat.md).

---

## Retire a skill

Retire a skill when it is no longer the best solution:

- It is no longer used.
- Its job is better handled by a script, an MCP server, or another skill.
- It has grown too many unrelated concerns and splitting would not help.
- A newer version or a different skill replaces it.

When retiring:

1. Mark the skill as deprecated in `SKILL.md` and `skills.json`.
2. Document the replacement path.
3. Update skills that depended on it.
4. After a reasonable transition period, remove the skill directory or move it to an archive.

See [`../../../guides/migrate-a-skill.md`](../../../guides/migrate-a-skill.md) and [`../lifecycle/deprecate-or-split.md`](../lifecycle/deprecate-or-split.md).

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
