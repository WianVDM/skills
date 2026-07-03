---
name: write-a-skill
description: Design, create, review, and upgrade agent skills according to project skill standards. Use when creating a new skill, refactoring an existing skill, reviewing a skill against conventions, deciding whether a problem deserves a skill, or upgrading a project-specific skill to global.
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "3.0"
---

# write-a-skill

This is a **conductor skill** that helps design, create, review, and upgrade agent skills. It ensures every skill follows the project skill standards by walking the user through a structured design process before any files are written.

A skill is a compact operating philosophy for a domain. This skill makes sure the user knows what they are building, why, and how it fits into the broader skill library — before implementation begins.

## Purpose

Help the user produce skills that are:

- Focused on one core objective.
- Portable and composable.
- Self-configuring and self-improving.
- Built through delegation and shared context.
- Validated against the project skill standards.

## When to use

- Creating a new skill from scratch.
- Refactoring an existing skill.
- Reviewing a skill against project skill standards.
- Deciding whether a problem deserves a skill or a simpler solution.
- Upgrading a project-specific skill to global status.
- Adding configuration, context sharing, delegation, or scripts to a skill.

## Out of scope

- This skill does not write production application code.
- It does not replace the user's judgment on whether a skill is needed.
- It does not perform destructive changes without user confirmation.

## Phases of engagement

The conductor moves through a series of design phases. It delegates focused work to subagents, integrates their findings, and never implements before the design is confirmed.

### Phase 1: Clarify intent

Understand what the user wants and whether a skill is the right solution.

- What problem is the user trying to solve?
- What triggered the request?
- What would success look like?

Delegate to [intent-analyzer](subagents/intent-analyzer.md) when the request is vague or when alternatives might exist.

### Phase 2: Classify the skill

Determine the shape of the skill before designing it.

- Skill type: standalone / atomic, building-block / vocabulary, conductor / orchestrator, or hybrid.
- Portability target: global or project-specific.
- Core objective and boundaries.
- Autonomy level: how much should the skill decide vs consult.

Delegate to [skill-classifier](subagents/skill-classifier.md).

### Phase 3: Explore alternatives

Before committing to a new skill, consider whether an existing skill, tool, MCP server, prompt template, or script already solves the problem.

Delegate to [alternative-advisor](subagents/alternative-advisor.md).

### Phase 4: Design the skill

Produce a structured design artifact covering:

- Objective and boundaries.
- Skill type and portability.
- Config needs and bootstrap behavior.
- Context interface: reports produced and consumed.
- Delegation strategy: subagents, other skills, or tools.
- Script inventory: deterministic checks or detections.
- State lifecycle if stateful.
- Security considerations.

Delegate to [skill-architect](subagents/skill-architect.md).

### Phase 5: Curate scripts

Identify where repeatable logic should live in deterministic scripts rather than AI inference.

Delegate to [script-curator](subagents/script-curator.md).

### Phase 6: Assess global readiness

If the skill is project-specific, identify what blocks it from being global and what it would take to remove those blockers.

Delegate to [global-readiness-assessor](subagents/global-readiness-assessor.md).

### Phase 7: Audit against guidelines

Check the design against the skill standard references and produce a review report.

Delegate to [guideline-auditor](subagents/guideline-auditor.md).

### Phase 8: Confirm with the user

Present the design and audit. Do not proceed to implementation until the user confirms or revises the design.

### Phase 9: Draft the skill

Once confirmed, produce the skill files: `SKILL.md`, `README.md`, references, subagents, scripts, assets, and templates.

Delegate to [skill-drafter](subagents/skill-drafter.md).

### Phase 10: Validate and close

Run a final audit on the drafted files, capture any gaps, and ask the user whether to iterate or finish.

## State and artifacts

This skill maintains working state to survive context compaction and resume later.

| Artifact | Location | Purpose |
|----------|----------|---------|
| Intent note | `.agents/context/skill-design/{skill-name}-intent.md` | Captured user intent and trigger. |
| Design draft | `.agents/context/skill-design/{skill-name}-design.md` | Structured skill design. |
| Review report | `.agents/context/skill-review/{skill-name}-review.md` | Skill standard audit results. |
| Global readiness report | `.agents/context/skill-review/{skill-name}-global-readiness.md` | Blockers to global portability. |
| Decision log | `.agents/context/skill-design/{skill-name}-decisions.md` | Record of decisions and rationale. |

Update these artifacts as decisions are made. Append decisions rather than overwriting them.

## User interaction rules

- Ask questions one at a time when the answer shapes later decisions.
- Present recommendations, not just options.
- Be explicit about assumptions and blockers.
- Pause and consult the user when ambiguity would require a guess.
- Never implement before confirming the design.

## References

- [What is a skill](../docs/skill-standards/01-what-is-a-skill.md)
- [Skill types](../docs/skill-standards/02-skill-types.md)
- [Form and style](../docs/skill-standards/03-form-and-style.md)
- [Structure and progressive disclosure](../docs/skill-standards/04-structure.md)
- [Common mistakes](../docs/skill-standards/05-common-mistakes.md)
- [When to create a skill](../docs/skill-standards/06-when-to-create-a-skill.md)
- [Global vs project-specific skills](../docs/skill-standards/07-global-vs-project-skills.md)
- [State](../docs/skill-standards/08-state.md)
- [Configuration](../docs/skill-standards/09-configuration.md)
- [Context and reports](../docs/skill-standards/10-context-and-reports.md)
- [Delegation](../docs/skill-standards/11-delegation.md)
- [Reusability](../docs/skill-standards/12-reusability.md)
- [Evaluation](../docs/skill-standards/13-evaluation.md)
- [Skill lifecycle](../docs/skill-standards/14-skill-lifecycle.md)
- [Examples](../docs/skill-standards/15-examples.md)
- [Security](../docs/skill-standards/16-security.md)
- [Dependencies](references/DEPENDENCIES.md)
