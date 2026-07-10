# Skill fundamentals (condensed)

> **This is a condensed fallback.** The canonical skill fundamentals live in `docs/skill-standards/fundamentals/`. If that directory is available, prefer it and treat this file as a degraded copy for projects that ship without the full standards wiki.
> Last synced: 2026-07-08.

## What a skill is

A skill is the smallest load-bearing shape that makes an agent reliably do the right thing for a specific domain. It is a contract between the author and the agent, not a script, prompt, or manual.

A skill is not a script, MCP server, prompt template, rule, or application code. It may contain or call those things, but its purpose is to shape the agent's behavior predictably.

## Skill types

| Type | Use when | Example |
|---|---|---|
| **Building block** | One narrow, reusable capability consumed by other skills. | `find-skills`, `audit-skill` |
| **Conductor** | Coordinates multiple tools, skills, or subagents through phases. | `write-a-skill`, `debrief` |
| **Wrapper** | Adapts another skill for human interaction. | Human-facing concierge over a building block |
| **Multi-layer / hybrid** | Combines layers with one clear primary role. | A conductor that also exposes a reusable report building block |

## Non-negotiables

- **Identity.** Every `SKILL.md` declares `name`, `description` (≤ 1024 chars, trigger-rich), and `invocation` (`model-invoked` or `user-invoked`). Add `version` once the skill is shared, consumed, or versioned.
- **Scope.** One core objective, explicit in-scope and out-of-scope items.
- **Form and style.** Load-bearing minimalism; checkable completion criteria; leading words; negation pairs; harness-agnostic and project-agnostic language; progressive disclosure.
- **Structure.** `SKILL.md` + `README.md` for non-trivial skills; optional `references/`, `subagents/`, `scripts/`, `assets/`, `config.yaml` only when needed.
- **Security.** No secrets in files; destructive actions confirmed; fail closed when a required capability is missing; prefer read-only inspection in untrusted projects.
- **Dependencies.** Declare all dependencies (skills, native tools, MCP servers, binaries, environment variables) as required, recommended, or optional. Check required dependencies eagerly; evaluate recommended and optional ones lazily. Declare the full surface in `references/DEPENDENCIES.md` and `skills.json`. Dependency categories include skill adapters, MCP tools/servers, native binaries, direct APIs, harness tools, and manual fallbacks.
- **Evaluation.** Model-invoked skills need trigger evals (10 should-trigger, 10 should-not-trigger). Behavioral evals compare with-skill vs. baseline output. Composable skills need composition tests. Discipline skills need pressure tests.
- **Portability.** The portable core is `SKILL.md` + optional siblings. Global skills detect the environment or ask the user. Degrade gracefully when the harness lacks a feature.
- **Tooling awareness.** A skill reasons in capabilities, not adapters. It detects the tools that can fulfill each capability, selects the best available one, and discloses the choice. If it uses a degraded source, it tells the user what better option was available and gets consent.
- **Colocation by default.** A capability should live inside the skill that owns it unless extraction is justified by reuse: cross-cutting concern, multiple current consumers, stable narrow interface, or generic-domain problem. Do not extract a skill simply because it is self-contained.

## Canonical source

For the full, maintained version of these fundamentals, see `docs/skill-standards/fundamentals/` and `docs/skill-standards/reference/sources.md`.

Update this fallback only after the canonical docs change, and only to the minimum needed for self-contained operation.
