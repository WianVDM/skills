# Skill Architecture Library — Architecture

## At a glance

This manifesto maps skills into a layered architecture: a portable core of `SKILL.md` plus sibling directories, a package envelope, and a trust layer. It defines the three primary skill layers (building block, conductor, wrapper), a hybrid category, and the cross-cutting patterns that apply to any layer.

**Read this if:** you need to choose a skill shape, design a composition, or understand how skills sit in the agent context stack.

## Overview

The library organizes skills into layers. Each layer has a single consumer and a single responsibility. A skill may participate in one or more layers, but its primary role should be clear.

The architecture is built on a **portable core**: a `SKILL.md` file with YAML frontmatter and a markdown body, plus optional sibling directories. Around this core sits a **package envelope** (`skills.json`, `skills.lock`, versioning, namespacing, dependencies) and a **trust layer** (provenance, evaluation, audit). The architecture is harness-agnostic: it can degrade gracefully for harnesses that only support a subset of the standard.

## The context stack

A consistent layered model emerges across agent harnesses. Skills are the on-demand, reusable layer in the stack.

| Layer | Examples | Purpose |
|-------|----------|---------|
| **Always-on context** | `AGENTS.md`, `CONVENTIONS.md`, `.cursorrules` | Project baseline, team conventions |
| **Scoped rules** | `.claude/rules`, `.cursor/rules/*.mdc` | File-type or situation-specific guidance |
| **Skills** | `SKILL.md` | Reusable, on-demand workflows and reference |
| **Hooks** | `PreToolUse`, `PostToolUse`, `SessionStart` | Deterministic lifecycle enforcement |
| **MCP / tools** | External servers, APIs | Capabilities the skill can call |
| **Subagents / crews** | Isolated workers | Delegation and coordination |

Skills are not the same as rules, context files, hooks, or MCP servers. A context file is always-on guidance; a rule is scoped guidance; a skill is a reusable, on-demand workflow. A hook enforces deterministic lifecycle events; an MCP server exposes a structured capability. A skill may invoke any of the lower layers, but it should not blur into them.

## The portable core

Every skill has a portable core that should be intelligible across harnesses:

```text
skill-name/
├── SKILL.md                 # required: identity + body
├── README.md                # for human maintainers
├── references/              # disclosed detail: schemas, examples, edge cases
├── subagents/               # worker personas for delegation
├── scripts/                 # deterministic helpers
└── assets/                  # templates, samples, fonts, images
```

- `SKILL.md` is the only required file. It contains the frontmatter (identity, routing, metadata) and the body (contract, steps, guidelines).
- `README.md` is for humans; the agent should not need it.
- `references/` holds detail that is too deep for `SKILL.md`.
- `subagents/` holds worker prompts for conductors and multi-layer skills.
- `scripts/` holds deterministic, repeatable logic that is cheaper and more reliable than asking the agent to regenerate it.
- `assets/` holds static resources, especially for non-coding skills.

Everything beyond this core — exact tool scoping, MCP server wiring, sandbox mode, subagent spawning, and native harness discovery — is **harness-specific envelope**. The standard defines the core and the envelope boundary, not the envelope itself.

## The package envelope

Skills that are shared, versioned, or have dependencies need a package envelope:

- `skills.json` — package metadata, dependencies, harness compatibility, required tools, MCP servers, and verification level.
- `skills.lock` — resolved dependency graph and content hashes.
- Versioning and namespacing — so consumers can depend on a stable contract.
- Dependency declarations — other skills, external tools, MCP servers, binaries, environment variables.

A standalone single skill can be a package of one. A package of multiple skills is namespaced under its package name.

## The three primary layers (and one hybrid)

### Layer 1: Building block

A building block is a narrow, reusable skill focused on one core objective. It has a clear interface and produces structured output that other skills can consume.

- **Primary consumer:** anyone, but usually the model or a conductor.
- **Shape:** minimal `SKILL.md`, one contract, one output format.
- **Rule:** if it does more than one thing, split it.

A building block is not defined by being model-invoked. It is defined by having a stable, narrow interface. A building block can be user-invoked and still be a building block (e.g., a shared vocabulary skill).

### Layer 2: Conductor

A conductor skill exists to coordinate other tools toward a larger objective. It delegates rather than doing the deep work itself.

- **Primary consumer:** the model, on behalf of the user.
- **Shape:** a pipeline, workflow, or set of phases.
- **Tools it can use:** skills, scripts, IDE extensions, MCP servers, third-party tools, subagents.
- **Rule:** a conductor is defined by orchestration, not by the number of tools it uses.

### Layer 3: Wrapper

A wrapper skill is a thin, user-facing layer that adapts a building block or conductor for human interaction. It adds prompts, presentation, and confirmation.

- **Primary consumer:** the human user.
- **Shape:** user-invoked, small, focused on interface.
- **Rule:** a wrapper should not contain core logic that belongs in the building block or conductor it wraps.

A wrapper is not a conductor. If it starts coordinating phases or maintaining state, it should be promoted to a conductor.

### Multi-layer / hybrid

A skill may participate in more than one layer, but its primary role should be clear. A multi-layer or hybrid skill combines layers around a single primary responsibility — for example, a conductor that also produces a reusable report, or a building block with a small internal workflow.

If the shape is unclear, the skill is not well-defined yet.

## Cross-cutting patterns

These patterns can appear in any of the primary layers or in a hybrid skill:

- **Discipline skill** — a prescriptive pattern that requires anti-rationalization design and pressure testing (e.g., test-driven development, verification-before-completion).
- **Context-file pattern** — always-on guidance that is not a skill. It lives in the always-on layer of the context stack.
- **Mode pattern** — a transient behavior switch (e.g., reasoning mode vs. execution mode).
- **Conductor/implementer split** — a role separation where one skill reasons and delegates, and another executes. This is a cross-cutting specialization of the conductor pattern.

## Architecture fundamentals

These concerns apply to any skill that participates in the architecture: skills that are shared, composed, distributed, portable, or otherwise used beyond a single local context. They are not universal core fundamentals, but they are required once a skill crosses the architecture boundary.

- **Tooling awareness** — capability-first tool selection, discovery, and degradation disclosure.
- **Security** — no secrets in files, confirm destructive actions, stay safe in untrusted projects.
- **Dependencies and bundling** — declare required, recommended, and optional dependencies; handle transitive closure and lazy evaluation.
- **Evaluation** — prove the skill improves behavior through trigger, behavior, composition, and pressure tests.

## Architecture-specific patterns

Skills that participate in the library architecture adopt only the patterns they need:

- **Global / pluggable** — detect environment, declare dependencies, avoid hardcoded paths, fail closed.
- **Configurable** — load config, handle first-run initialization, persist notes.
- **Initialization** — first-run setup for global or configurable skills.
- **Stateful** — persist state across invocations or context compaction.
- **Context reports** — produce and consume structured reports with clear contracts and freshness rules.
- **Versioning** — version bumping and migration paths when a skill is consumed by others.

## Composition and delegation

A conductor may use any of the following:

- **Skills** — building blocks and wrappers in the library.
- **Scripts** — deterministic helpers attached to a skill.
- **Extensions** — IDE or environment extensions.
- **MCP servers** — external tools reachable through a protocol.
- **Third-party tools** — anything else the conductor needs.
- **Subagents** — isolated workers for focused tasks.

If a script, extension, MCP server, or third-party tool is reused across conductors, consider wrapping it as a skill. A skill is the preferred interface for reusable, judgment-shaped guidance.

## State, config, reports, and notes

The architecture defines well-known locations for cross-cutting concerns:

```text
{project-root}/
├── .agents/
│   ├── config/
│   │   ├── shared.yaml
│   │   └── {skill-name}.yaml
│   ├── context/
│   │   ├── {skill-name}/           # stateful skill state
│   │   │   └── {key}/
│   │   ├── {report-type}/          # context reports
│   │   │   └── {key}.md
│   │   └── handoffs/               # session handoffs
│   └── skills/                     # installed skills
│       └── {skill-name}/
```

- **Config** separates invariant principles from project-specific preferences.
- **State** lets a skill survive context compaction or multi-session work.
- **Reports** let skills share structured findings without being tightly coupled.
- **Notes** capture operational memory and discovered preferences.

## Choosing a shape

Ask these questions in order:

1. Does it do one narrow, well-bounded thing? → **Building block.**
2. Does it coordinate other tools to reach a larger goal? → **Conductor.**
3. Does it adapt another skill for a human? → **Wrapper.**
4. Does it combine layers with a clear primary role? → **Multi-layer / hybrid.**

If the answer is unclear, the skill is not well-defined yet.

## Key takeaways

- Skills are the **on-demand, reusable layer** in the agent context stack, between always-on context and tools.
- The **portable core** is harness-agnostic; the **envelope** is harness-specific.
- Choose a primary shape based on responsibility: **building block** (narrow capability), **conductor** (coordination), **wrapper** (human-facing adaptation), or **multi-layer / hybrid** when a clear primary role still exists.
- **Cross-cutting patterns** (discipline, context-file, mode, conductor/implementer split) can appear in any layer.
- **Architecture fundamentals** (tooling awareness, security, dependencies, evaluation) apply once a skill crosses the architecture boundary.
- **Composition** uses skills, scripts, MCP servers, extensions, third-party tools, and subagents.
- **State, config, reports, and notes** live in well-known `.agents/` locations.
- If the shape is unclear, the skill is not well-defined yet.

## Research basis

- **Context stack** — The layered model of always-on context, scoped rules, skills, hooks, MCP, and subagents is drawn from comparing Claude Code, Cursor, Codex, Aider, and Hermes. See the rules-context-files-skills-boundary correlation in the research corpus.
- **Portable core** — Claude Code, Cursor, Codex, Aider, and Hermes all converge on a markdown skill file with a routing description and a body of guidance. The agentskills.io specification defines a minimal frontmatter surface. https://agentskills.io/specification
- **Package envelope** — Codex, Claude Code, Hermes, and the agentskills.io ecosystem all support package-level metadata, versioning, and dependency declaration. The standard's envelope is a design decision synthesized from these systems.
- **Building block / conductor / wrapper** — This taxonomy is our own choice, but it is supported by the research on skill taxonomies and the need to separate narrow capabilities from coordination and presentation.
- **Cross-cutting patterns** — Discipline skills, context files, modes, and the conductor/implementer split are drawn from obra/superpowers, Aider, and the broader practitioner literature.
- **Architecture fundamentals** — Tooling awareness, security, dependencies, and evaluation are synthesized from the research on tool selection, governance, and cross-harness skill quality.
- **State and context conventions** — The `.agents/config` and `.agents/context` layout is our own convention, aligned with the research emphasis on context cost, memory, and structured handoffs.
- **Limitations** — Exact trigger thresholds, rule-vs-skill precedence, and harness-specific envelope details are proprietary or rapidly changing, so they are documented as limitations rather than core architecture.
