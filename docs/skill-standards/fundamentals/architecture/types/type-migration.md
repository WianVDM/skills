# Type migration

**Layer:** proposed architecture. **Mode:** guide.

A skill's primary layer can change as it matures:

- A building block that grows workflow phases may become a conductor.
- A conductor whose value is mostly a reusable report may split into a conductor and a building block.
- A wrapper that starts coordinating multiple skills may become a conductor with a thin wrapper on top.
- A piece of reference repeated across several skills may be extracted into a building block.

When a skill changes type, its structure and invocation mode should change too. Do not keep a user-invoked shell around a conductor's internals, or a model-invoked description on a skill that no longer needs discovery.

See [`../failure-recovery/split-prune-retire.md`](../../core/failure-recovery/split-prune-retire.md) for the operational side of splitting and retiring skills and [`../../../guides/migrate-a-skill.md`](../../../guides/migrate-a-skill.md) for migration steps.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
