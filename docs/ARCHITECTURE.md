# Skill Architecture Library — Architecture

## Overview

The library pattern organizes skills into three layers. Each layer has a single consumer and a single responsibility. A skill may participate in one or more layers, but its primary role should be clear.

## The three layers

### Layer 1: Building block

A barebones skill focused on one core objective. It has no presentation layer, no workflow, and no assumptions about who calls it.

- **Primary consumer:** anyone, but usually the model.
- **Shape:** minimal `SKILL.md`, one contract, one output format.
- **Rule:** if it does more than one thing, split it.

### Layer 2: Conductor

A skill that exists to coordinate other tools toward a larger objective. It delegates rather than doing the work itself.

- **Primary consumer:** the model.
- **Shape:** a pipeline, workflow, or set of phases.
- **Tools it can use:** skills, scripts, IDE extensions, MCP servers, third-party tools.
- **Rule:** a conductor is defined by orchestration, not by the number of tools it uses.

### Layer 3: Wrapper

A thin skill that exists to adapt another skill or conductor for user interaction. It adds prompts, presentation, and user confirmation.

- **Primary consumer:** the user.
- **Shape:** user-invoked, small, focused on interface.
- **Rule:** a wrapper should not contain core logic that belongs in a building block or conductor.

## Tool taxonomy

A conductor may use any of the following:

- **Skills** — building blocks and wrappers in the library.
- **Scripts** — deterministic helpers, often attached to a skill.
- **Extensions** — IDE or environment extensions.
- **MCP servers** — external tools reachable through a protocol.
- **Third-party tools** — anything else the conductor needs.

If a script, extension, MCP server, or third-party tool is reused across conductors, consider wrapping it as a skill.

## Patterns

The architecture layer contains optional patterns that a skill adopts when it needs them:

- **Global / pluggable** — detect environment, declare dependencies, avoid hardcoded paths, fail closed.
- **Configurable** — load config, handle first-run initialization, persist notes.
- **Context sharing** — produce and consume structured reports with clear contracts and freshness rules.
- **Versioning** — version bumping and migration paths when a skill is consumed by others.
- **Security** — no secrets in files, confirm destructive actions, stay safe in untrusted projects.

A skill chooses only the patterns it needs. A simple building block may need none of them.

## Choosing a shape

Ask these questions in order:

1. Does it do one narrow thing? → **Building block.**
2. Does it coordinate other tools to reach a larger goal? → **Conductor.**
3. Does it adapt another skill for a human? → **Wrapper.**

If the answer is unclear, the skill is not well-defined yet.
