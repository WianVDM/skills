# SKILL.md

**Layer:** universal fundamentals. **Mode:** rule.

`SKILL.md` is the skill's public interface. It should contain only what the agent needs on every invocation.

A good `SKILL.md` answers:

- What does this skill do?
- When should it run?
- What is the core contract?
- What is in and out of scope?
- Where does detailed reference live?

Push deep detail into `references/`. Push worker prompts into `subagents/`. Push deterministic logic into `scripts/`.

See [`./frontmatter.md`](./frontmatter.md) for the identity and invocation declarations and [`../form-and-style/`](../form-and-style/) for how to write the body.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
