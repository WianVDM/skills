# Skill Standards

This package is the practical companion to the top-level manifestos:

- [`docs/PHILOSOPHY.md`](../PHILOSOPHY.md) — *why* we build skills this way.
- [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) — the structural shape of the library: layers, taxonomy, patterns, composition.
- [`docs/PORTABILITY.md`](../PORTABILITY.md) — how the portable core degrades gracefully across agent harnesses.

Those documents are short, abstract, and stable. **This package is the wiki that unpacks them.** It contains the specific language, rules, patterns, examples, and lookup tables that turn the manifestos into working skills.

Use this document as the starting point whenever you need to:

- Write a new skill.
- Review or refactor an existing skill.
- Decide whether a capability belongs in a skill, a script, an MCP server, or plain inference.
- Understand how the library's composable patterns fit together.

---

## What a skill is

A skill is the **smallest load-bearing shape** that makes an agent reliably do the right thing for a specific domain. It is a **contract** between the skill author and the agent, not a script, manual, or prompt.

See [`fundamentals/what-is-a-skill.md`](./fundamentals/what-is-a-skill.md) for the full definition, root virtues, and failure modes.

---

## The standards package

The package is organized into layers. The boundary is not about importance; it is about **scope**. A skill must satisfy the fundamentals. It adopts patterns only when the skill's role requires them.

### Format and package

- [`FORMAT.md`](./FORMAT.md) — the `SKILL.md` core: frontmatter, body, sibling directories, and harness-agnostic rules.
- [`PACKAGE.md`](./PACKAGE.md) — `skills.json`, `skills.lock`, versioning, namespacing, dependencies, lifecycle, and formal JSON schemas.
- `schemas/` — JSON Schema files for `SKILL.md` frontmatter, `skills.json`, `evals.json`, and `skills.lock`. See `schemas/README.md`.

### Fundamentals (universal)

Every skill must satisfy these.

| Fundamental | Document | What it covers |
|---|---|---|
| **What is a skill?** | [`fundamentals/what-is-a-skill.md`](./fundamentals/what-is-a-skill.md) | Definition, root virtues, failure modes. |
| **Types** | [`fundamentals/types.md`](./fundamentals/types.md) | Building block, conductor, wrapper, multi-layer. |
| **Structure** | [`fundamentals/structure.md`](./fundamentals/structure.md) | `SKILL.md`, `references/`, `scripts/`, `subagents/`, `assets/`, progressive disclosure. |
| **Form and style** | [`fundamentals/form-and-style.md`](./fundamentals/form-and-style.md) | Steps, guidelines, completion criteria, leading words, pruning. |
| **Common mistakes** | [`fundamentals/common-mistakes.md`](./fundamentals/common-mistakes.md) | Bloat, sediment, duplication, no-op instructions, hidden dependencies. |
| **Evaluation** | [`fundamentals/evaluation.md`](./fundamentals/evaluation.md) | Trigger evals, predictability tests, review checklists. |
| **Lifecycle** | [`fundamentals/lifecycle.md`](./fundamentals/lifecycle.md) | Draft, test, publish, maintain, retire. |
| **Security** | [`fundamentals/security.md`](./fundamentals/security.md) | Secrets, destructive actions, required capabilities, fail closed. |
| **When to create a skill** | [`fundamentals/when-to-create-a-skill.md`](./fundamentals/when-to-create-a-skill.md) | Skill vs. script, MCP server, prompt template. |

### Patterns (opt-in)

A skill adopts these only when its role requires them.

| Pattern | Document | When to adopt |
|---|---|---|
| **Building block** | [`patterns/building-block.md`](./patterns/building-block.md) | Reusable capability with a narrow interface. |
| **Conductor** | [`patterns/conductor.md`](./patterns/conductor.md) | Coordination of multiple skills/tools through phases. |
| **Wrapper** | [`patterns/wrapper.md`](./patterns/wrapper.md) | Adapt a skill for human interaction. |
| **Discipline skill** | [`patterns/discipline-skill.md`](./patterns/discipline-skill.md) | Anti-rationalization, pressure-tested guidance. |
| **Context-file** | [`patterns/context-file.md`](./patterns/context-file.md) | Always-on guidance that is not a skill. |
| **Mode** | [`patterns/mode.md`](./patterns/mode.md) | Transient behavior switch. |
| **Conductor/implementer split** | [`patterns/conductor-implementer-split.md`](./patterns/conductor-implementer-split.md) | Separate reasoning from execution. |
| **Global / pluggable** | [`patterns/global-pluggable.md`](./patterns/global-pluggable.md) | Work in any project, harness, or user context. |
| **Configurable** | [`patterns/configurable.md`](./patterns/configurable.md) | Per-project or per-user preferences. |
| **Initialization** | [`patterns/initialization.md`](./patterns/initialization.md) | First-run setup for global/configurable skills. |
| **Stateful** | [`patterns/stateful.md`](./patterns/stateful.md) | Persist state across invocations. |
| **Context reports** | [`patterns/context-reports.md`](./patterns/context-reports.md) | Produce or consume structured reports. |
| **Versioning** | [`patterns/versioning.md`](./patterns/versioning.md) | Consumers depend on the skill's behavior or schema. |

### Cross-cutting concerns

- [`GOVERNANCE.md`](./GOVERNANCE.md) — provenance, agent-authored skills, staging, approval, verification levels, audit.
- [`EVALUATION.md`](./EVALUATION.md) — the `evals/evals.json` framework, runner interface, baselines, composition tests.
- [`EXTENSIBILITY.md`](./EXTENSIBILITY.md) — non-coding skills and multi-agent coordination.
- [`MIGRATION.md`](./MIGRATION.md) — moving a skill between shapes (project-specific → global, rule → skill, v1 → v2).
- [`TRIGGER_EVALS.md`](./TRIGGER_EVALS.md) — practical guide and template for testing skill routing.
- [`CONTEXT_BUDGET.md`](./CONTEXT_BUDGET.md) — description length, splitting, and context-load management.

### Quick references

- [`QUICKREF.md`](./QUICKREF.md) — one-page summaries for authors, reviewers, and consumers.
- [`PATTERN_CATALOG.md`](./PATTERN_CATALOG.md) — which patterns compose with which.

---

## Taxonomy

### By layer

| Layer | Consumer | Responsibility | Example |
|---|---|---|---|
| Building block | anyone, usually the model | one narrow capability | `find-skills`, `install-skill` |
| Conductor | the model | coordinates tools through phases | `debrief`, `orchestrate` |
| Wrapper | the user | adapts another skill for human use | a find-and-install concierge |

### By invocation

| Invocation | Reached by | Cost | Use when |
|---|---|---|---|
| Model-invoked | agent or other skills | context load | the skill must fire autonomously or be reached by other skills |
| User-invoked | human by name | cognitive load | the skill only fires when the user explicitly asks |

### By composition

| Relationship | Description |
|---|---|
| Standalone | a skill that works alone and has no required consumers |
| Composable | a skill designed to be reached by other skills or conductors |
| Multi-layer | a skill that participates in more than one layer, with a clear primary role |

---

## Decision guide

### I am writing a new skill

1. Read [`fundamentals/what-is-a-skill.md`](./fundamentals/what-is-a-skill.md) and [`fundamentals/types.md`](./fundamentals/types.md).
2. Choose the right type: building block, conductor, or wrapper.
3. Draft the smallest viable `SKILL.md` using [`FORMAT.md`](./FORMAT.md) and [`fundamentals/structure.md`](./fundamentals/structure.md).
4. Check [`fundamentals/common-mistakes.md`](./fundamentals/common-mistakes.md) before expanding.
5. If the skill is global, configurable, stateful, report-producing, reusable, or versioned, read the relevant pattern docs.
6. Review against [`fundamentals/evaluation.md`](./fundamentals/evaluation.md).

### I am reviewing an existing skill

1. Does it satisfy the fundamentals? Start with [`fundamentals/evaluation.md`](./fundamentals/evaluation.md).
2. Is it the right type? See [`fundamentals/types.md`](./fundamentals/types.md).
3. Is it bloated? See [`fundamentals/common-mistakes.md`](./fundamentals/common-mistakes.md).
4. Does it adopt architecture patterns correctly? See the relevant pattern docs.

### I am deciding whether to create a skill

1. See [`fundamentals/when-to-create-a-skill.md`](./fundamentals/when-to-create-a-skill.md).
2. If the problem is better solved by a script, MCP server, or plain inference, do not create a skill.

### I want a skill to be global

1. Read [`patterns/global-pluggable.md`](./patterns/global-pluggable.md) and [`docs/PORTABILITY.md`](../PORTABILITY.md).
2. Add detection and config using [`patterns/configurable.md`](./patterns/configurable.md) and [`patterns/initialization.md`](./patterns/initialization.md).
3. Declare dependencies and fail closed.

### I want a skill to compose other skills

1. Read [`patterns/conductor.md`](./patterns/conductor.md).
2. Use [`patterns/building-block.md`](./patterns/building-block.md) to identify reusable pieces.
3. Use [`patterns/context-reports.md`](./patterns/context-reports.md) for shared artifacts.

### I want to expose a skill to the user with prompts and confirmation

1. Read [`patterns/wrapper.md`](./patterns/wrapper.md).
2. Keep core logic in the building block or conductor being wrapped.

### I want to migrate or evolve a skill

1. See [`MIGRATION.md`](./MIGRATION.md) for the common shape changes.
2. Update the `version` and `provenance` metadata if the contract or schema changed.
3. Re-run trigger and behavioral evals after the migration.

---

## Glossary

See [`GLOSSARY.md`](./GLOSSARY.md) for precise definitions of terms used across the standards.

Key terms to know before reading the subdocuments:

- **Predictability** — the root virtue; the skill makes the agent follow the same process every time.
- **Load-bearing minimalism** — every line must earn its place.
- **Context pointer** — a reference that names out-of-context material and when to reach for it.
- **Progressive disclosure** — moving detail behind pointers so the top level stays legible.
- **Leading word** — a compact concept that anchors behavior in the model's priors.
- **Completion criterion** — a checkable condition that tells the agent a step is done.
- **Fail closed** — stop and explain when a required capability is missing.
- **Building block** — a narrow, reusable skill consumed by others.
- **Conductor** — a skill that coordinates other skills through phases.
- **Wrapper** — a thin skill that adapts another skill for human interaction.

---

## Continuous refinement

These standards are not final. As the library grows and we learn what works, the standards will change. A skill that followed the standards at version 1.0 may need to be updated to follow version 2.0.

When a standard changes, update the skills it affects. Do not keep a rule just because it was written down. The goal is reliable skills, not compliance for its own sake.

---

## Research basis

The standards are synthesized from:

- Harness makers: Claude Code (https://code.claude.com/docs/en/skills), Cursor (https://cursor.com/docs/skills), Codex (https://developers.openai.com/codex/guides/agents-md), Aider (https://aider.chat/docs/), Hermes (https://github.com/NousResearch/hermes-agent).
- Infrastructure: MCP (https://modelcontextprotocol.io/specification).
- Skill registry specifications: agentskills.io (https://agentskills.io/specification).
- Practitioners: Matt Pocock, obra/superpowers, Simon Willison, Andrej Karpathy.
- Academic and systematic analyses: *Skills as Verifiable Artifacts* (arXiv 2605.00424), *Beyond Human-Readable*, *Dive into Claude Code*.
- Our own design choices: the building block / conductor / wrapper taxonomy, the two-layer standards split, and the "smallest load-bearing shape" framing.

Specific claims are attributed in the relevant subdocuments. Many details remain **limited**: proprietary harness internals, exact trigger thresholds, future tooling maturity, and subjective evaluation verdicts are documented as limitations rather than facts.
