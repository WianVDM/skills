# Skill standards

This wiki defines the core rules, patterns, and reference material for writing portable, composable, and predictable agent skills. It is a standalone specification: everything needed to read, write, review, or audit a skill is documented here.

## At a glance

**Layer:** proposed architecture. **Mode:** reference.

A **skill** is the smallest load-bearing shape that makes an agent reliably do the right thing for a specific domain. It is a **delegation boundary**: a contract that tells the agent what matters, what to watch for, and what shape the work should take. It is not a script, manual, prompt template, or configuration file.

The **root virtue** of a skill is **predictability**: the agent should follow the same *process* every time the skill runs. Output may vary, but behavior should not.

The standard is built around three layers:

1. **Portable core** — a `SKILL.md` file with YAML frontmatter and a markdown body, plus optional sibling directories (`references/`, `subagents/`, `scripts/`, `assets/`). This is the part that should work across agent harnesses.
2. **Package envelope** — `skills.json`, `skills.lock`, versioning, namespacing, and dependency declarations. This is needed once a skill is shared, consumed, or distributed.
3. **Trust layer** — evaluation and audit. A skill is not finished when it is written; it is finished when it reliably improves behavior.

## The context stack

Skills sit in a layered context model:

| Layer | Examples | Purpose |
|-------|----------|---------|
| **Always-on context** | `AGENTS.md`, `CONVENTIONS.md`, `.cursorrules` | Project baseline, team conventions |
| **Scoped rules** | `.claude/rules`, `.cursor/rules/*.mdc` | File-type or situation-specific guidance |
| **Skills** | `SKILL.md` | Reusable, on-demand workflows and reference |
| **MCP / tools** | External servers, APIs | Capabilities the skill can call |
| **Subagents / crews** | Isolated workers | Delegation and coordination |

A context file is always-on guidance. A rule is scoped guidance. A skill is a reusable, on-demand workflow. An MCP server exposes a structured capability. A skill may invoke lower layers, but it should not blur into them.

## Quick start

To write a skill:

1. Decide whether the task should be a **building block**, **conductor**, **wrapper**, or context file. See [`fundamentals/architecture/types/`](./fundamentals/architecture/types) and [`patterns/context-file.md`](./patterns/context-file.md).
2. Create a directory named after the skill (lowercase, hyphen-separated) and add a `SKILL.md` with required frontmatter (`name`, `description`, `invocation`) and a body that states purpose, scope, and contract. See [`reference/format.md`](./reference/format.md).
3. Push deep detail into `references/` and worker prompts into `subagents/`.
4. Declare dependencies in `references/DEPENDENCIES.md` or `skills.json`.
5. Write trigger and behavioral evals in `evals/evals.json`. See [`reference/evaluation-framework.md`](./reference/evaluation-framework.md) and [`guides/trigger-evals.md`](./guides/trigger-evals.md).

For a complete walkthrough, see [`guides/write-a-skill.md`](./guides/write-a-skill.md).

## Wiki sections

| Section | Purpose |
|---|---|
| [`fundamentals/`](./fundamentals) | Core and architecture fundamentals, and why the wiki is split that way. |
| [`fundamentals/core/`](./fundamentals/core) | Universal rules every skill must satisfy. |
| [`fundamentals/architecture/`](./fundamentals/architecture) | Opt-in rules for skills that participate in the architecture (shared, composed, distributed, portable). |
| [`patterns/`](./patterns) | Opt-in architecture shapes: building block, conductor, wrapper, and cross-cutting patterns. |
| [`guides/`](./guides) | Task-oriented guides: write, review, audit, migrate. |
| [`reference/`](./reference) | Format, package, evaluation, glossary, and lookup tables. |
| [`schemas/`](./schemas) | JSON schemas for skill frontmatter, package envelopes, and evals. |

---

## How to read this wiki

If you are new, start with this README, then read:

1. [`fundamentals/core/what-is-a-skill/`](./fundamentals/core/what-is-a-skill) — what a skill is and is not.
2. [`fundamentals/architecture/types/`](./fundamentals/architecture/types) — building block, conductor, wrapper, and multi-layer skills.
3. [`reference/format.md`](./reference/format.md) — the `SKILL.md` format and frontmatter.
4. [`fundamentals/architecture/`](./fundamentals/architecture) — once you are writing a shared or composable skill.

If you are reviewing or auditing a skill, see [`reference/audit-rubric.md`](./reference/audit-rubric.md) and [`guides/review-a-skill.md`](./guides/review-a-skill.md).

---

## Research basis

This standard is a synthesis of common denominators across agent harnesses and the broader agent-skills ecosystem. See [`reference/sources.md`](./reference/sources.md) for the research basis and attribution notes.
