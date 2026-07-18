# Skill fundamentals

**Layer:** proposed architecture. **Mode:** reference.

The `fundamentals/` directory is split into two groups. The split matches the architecture manifesto: some ideas are universal to every skill, and others are opt-in rules for skills that participate in the architecture (portability, composition, distribution, trust).

## `core/` — universal fundamentals

Every skill, even a single local `SKILL.md`, should satisfy these. They are about what a skill is, when to create one, and how to keep it focused and predictable.

See [`core/README.md`](./core/README.md) for the core topics and the suggested reading order.

## `architecture/` — opt-in architecture fundamentals

These matter when a skill is shared, composed, distributed, or otherwise participates in the architecture (portability, composition, trust). A standalone personal skill does not have to read them, but a skill that other skills consume or that runs across harnesses should.

See [`architecture/README.md`](./architecture/README.md) for the architecture topics and the suggested reading order.
