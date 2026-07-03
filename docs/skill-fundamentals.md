# Skill Fundamentals

This document package defines the fundamentals, standards, and evaluation criteria for writing effective agent skills. It is a reference for skill authors, not a skill itself.

Use these documents when designing a new skill, reviewing an existing one, or deciding whether a problem deserves a skill at all.

> This is groundwork. The standards here will evolve as the skill library grows and as we learn what makes skills reliable in practice.

---

## What a skill is

A skill is the **smallest load-bearing shape** that makes an agent reliably do the right thing for a specific domain.

It is not a script, not a manual, and not a prompt. It is a contract between the author and the agent about how to behave. The agent still decides the exact actions; the skill decides the shape of those actions.

See [01-what-is-a-skill.md](./skill-standards/01-what-is-a-skill.md) for the full definition and root virtues.

---

## The standards package

| Document | Purpose |
|----------|---------|
| [GLOSSARY.md](./skill-standards/GLOSSARY.md) | Definitions of terms used across all standards documents. |
| [01-what-is-a-skill.md](./skill-standards/01-what-is-a-skill.md) | Definition, root virtues, and what a skill is not. |
| [02-skill-types.md](./skill-standards/02-skill-types.md) | The four skill types and how to choose the right one. |
| [03-form-and-style.md](./skill-standards/03-form-and-style.md) | Step-by-step instructions vs guidelines vs hybrid, and when to use each. |
| [04-structure.md](./skill-standards/04-structure.md) | Files, folders, frontmatter, naming, and progressive disclosure. |
| [05-common-mistakes.md](./skill-standards/05-common-mistakes.md) | What makes skills unreliable, bloated, or ineffective. |
| [06-when-to-create-a-skill.md](./skill-standards/06-when-to-create-a-skill.md) | Skill vs script vs MCP server vs plain inference. |
| [07-global-vs-project-skills.md](./skill-standards/07-global-vs-project-skills.md) | Pluggability, portability, and what makes a skill global. |
| [08-state.md](./skill-standards/08-state.md) | Stateful vs stateless skills, state lifecycle, and checkpointing. |
| [09-configuration.md](./skill-standards/09-configuration.md) | Config location, schema, bootstrap, and notes. |
| [10-context-and-reports.md](./skill-standards/10-context-and-reports.md) | Shared context, report schema, and cross-skill consumption. |
| [11-delegation.md](./skill-standards/11-delegation.md) | When and how to delegate to subagents and workers. |
| [12-reusability.md](./skill-standards/12-reusability.md) | Building-block skills, shared references, and avoiding duplication. |
| [13-evaluation.md](./skill-standards/13-evaluation.md) | Checklists and review questions for every skill type. |
| [14-skill-lifecycle.md](./skill-standards/14-skill-lifecycle.md) | From idea to draft to test to publish to maintain. |
| [15-examples.md](./skill-standards/15-examples.md) | Concrete examples of skill shapes, config, reports, and workers. |
| [16-security.md](./skill-standards/16-security.md) | Secrets, destructive actions, external access, and fail-closed behavior. |

---

## How to use this package

1. Start with [01-what-is-a-skill.md](./skill-standards/01-what-is-a-skill.md) and [02-skill-types.md](./skill-standards/02-skill-types.md).
2. If you are unsure what shape a skill should take, read [03-form-and-style.md](./skill-standards/03-form-and-style.md).
3. Before writing files, check [04-structure.md](./skill-standards/04-structure.md).
4. Before deciding a problem needs a skill, read [06-when-to-create-a-skill.md](./skill-standards/06-when-to-create-a-skill.md).
5. For concrete patterns, see [15-examples.md](./skill-standards/15-examples.md).
6. For security considerations, see [16-security.md](./skill-standards/16-security.md).
7. Review against [13-evaluation.md](./skill-standards/13-evaluation.md) before considering a skill complete.
8. Follow [14-skill-lifecycle.md](./skill-standards/14-skill-lifecycle.md) for the full path from idea to maintenance.

---

## Core philosophy in one paragraph

A skill exists to wrangle determinism out of a stochastic system. **Predictability** is the root virtue: a skill should make the agent more predictable without removing its ability to reason. It should be as small as possible, as specific as necessary, and composable with other skills. It should declare what it needs, fail explicitly, and never silently assume.
