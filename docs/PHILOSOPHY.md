# Skill Architecture Library — Philosophy

## Mission

To define the smallest set of fundamentals that make any agent skill great, and to document a modular architecture pattern that lets skills be composed from reusable building blocks, conductors, and wrappers. This standard is both a specification and a living library of skills built on those principles.

A skill is a reusable unit of process guidance that is injected into an agent's context window to shape behavior predictably. It is not a prompt, not a script, not a plugin, and not a rule — though it can contain any of those things. The most useful framing is that a skill is a **delegation boundary**: it lets a human or team say "here is how this kind of work is done here," and then have that guidance travel with the agent across sessions, tasks, and (when portable) harnesses.

## Core beliefs

1. **A skill is the smallest load-bearing shape.**
   It should do one thing well and carry only what it needs. If removing a sentence, example, or step does not change behavior, remove it.

2. **Minimalism beats completeness.**
   A lean skill that is reliably invoked is better than a bloated skill that is ignored. Do not try to cover every edge case in the top-level `SKILL.md`. Push detail into `references/` and pull it in when needed.

3. **Fundamentals are universal; architecture is opt-in.**
   Every skill needs identity, focus, scope, and clarity. Only skills that want to be composed, shared, and reused need to adopt the architecture patterns.

4. **The model is a tool user too.**
   Skills can be invoked by humans, but the model should be able to use them as first-class tools. A building block skill can be reached by other skills and conductors. A conductor skill can compose building blocks.

5. **Composition over monoliths.**
   Complex behavior should emerge from simple skills composed together, not from one skill that does everything.

6. **Predictability is the root virtue.**
   A skill exists to wrangle determinism out of a stochastic system. The agent should follow the same *process* every time the skill runs. Output may vary, but behavior should not.

7. **Trust is built through provenance, evaluation, and audit.**
   If agents can write skills, then provenance, approval, and audit become first-class concerns. A skill without provenance metadata is not ready for distribution.

8. **Refinement is continuous.**
   Skills and standards are polished over time as we learn what works. We never keep a rule just because it was written down.

## What this standard is

- A place to document the core of what makes a skill great.
- A place to document a specific architecture pattern for composable, reusable skills.
- A place to develop skills that follow those principles.
- A place to define a portable core format that can degrade gracefully across agent harnesses.

## What this standard is not

- A generic prompt library.
- A one-size-fits-all framework.
- A fixed, unchanging specification.
- A place for skills that do not know what they are for.
- A harness-specific guide for any single tool or editor.

## How this standard evolves

We start with the smallest possible fundamentals and the smallest possible architecture. We add patterns only when a recurring need proves they are necessary. We change existing skills when the standards change. We document our limitations honestly rather than pretending to certainty.

## Research basis

This philosophy is a synthesis of common denominators from the agent-skills ecosystem and our own design choices:

- **Harness makers** — Claude Code, Cursor, Codex, Aider, and Hermes all converge on a markdown-based skill file with a routing description and a body of guidance. Their docs shape what is portable and what is harness-specific envelope.
  - Claude Code: https://code.claude.com/docs/en/skills
  - Cursor: https://cursor.com/docs/skills
  - Codex: https://developers.openai.com/codex/guides/agents-md
  - Aider: https://aider.chat/docs/
  - Hermes: https://github.com/NousResearch/hermes-agent
- **Infrastructure** — The Model Context Protocol (MCP) provides a tool layer that skills can invoke but does not replace skill logic. https://modelcontextprotocol.io/specification
- **Skill registry specifications** — The agentskills.io specification and validator define a portable skill frontmatter surface. https://agentskills.io/specification
- **Practitioners** — Matt Pocock, obra/superpowers, Simon Willison, and Andrej Karpathy have each emphasized skills as reusable process guidance, context discipline, and composition over monolithic prompts.
- **Academic and systematic analyses** — *Skills as Verifiable Artifacts* (arXiv 2605.00424) frames governance, provenance, and verification levels as first-class concerns. *Beyond Human-Readable* and *Dive into Claude Code* provide empirical and structural analysis of how skills interact with context and reasoning.
- **Our own design choices** — The building block / conductor / wrapper taxonomy, the two-layer standards split, and the "smallest load-bearing shape" framing are our own choices, made to keep the standard coherent and the library maintainable.

Many details remain **limited**: exact trigger thresholds, proprietary harness internals, future tooling maturity, and subjective evaluation verdicts are documented as limitations rather than facts.
