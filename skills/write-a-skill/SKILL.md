---
name: write-a-skill
description: Skill-design partner. Use when creating, reviewing, upgrading, or deciding whether a problem deserves a skill.
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "3.1"
  scope: global
invocation: user-invoked
disable-model-invocation: true
---

# write-a-skill

Use this skill as a design partner that will not draft files until the design and a self-audit pass the fundamentals.

## Purpose

Help the user produce skills that are:

- Focused on one core objective.
- Portable and composable.
- Self-configuring through detection and explicit config.
- Validated against the fundamentals before implementation.

## When to use

- **Create a new skill** from scratch.
- **Review an existing skill** against the fundamentals.
- **Upgrade a project-specific skill** toward global portability.
- **Decide whether a problem deserves a skill**, or whether a script, MCP server, extension, prompt template, or existing skill is enough.

## Out of scope

- This skill does not write production application code.
- It does not replace the user's judgment on whether a skill is needed.
- It does not perform destructive changes without explicit confirmation.
- It does not choose an alternative for the user without first exploring it.

## Portability and invocation

- **Invocation mode:** user-invoked. The skill is a meta-design conversation and should not stay loaded during normal work. The frontmatter declares both `invocation: user-invoked` and `disable-model-invocation: true` so the mode is unambiguous across harnesses.
- **Scope:** global. It must work in any project with any harness.
- **Pluggability:** the skill detects the project layout (skills directory, context directory, config directory) and **always confirms** with the user before writing files. See [references/PLUGGABILITY.md](references/PLUGGABILITY.md).
- **No hardcoded project paths:** paths are resolved through detection or user confirmation. The only acceptable hardcoded strings are the detection rules themselves.

## Branch entry

The first thing the conductor does is classify the user's intent into one branch. This keeps the workflow short and appropriate for the request. If the intent is unclear, ask one clarifying question with a proposed default.

| Branch | Trigger | Outcome |
|---|---|---|
| **New** | User wants to design a new skill from scratch. | Full design workflow + draft. |
| **Quick** | User wants a minimal skill based on a brief description. | Compressed design workflow + draft. |
| **Review** | User wants to audit an existing skill. | Audit report with ratings. |
| **Upgrade** | User wants to make a project-specific skill global-ready. | Remediation plan + optional changes. |

**Completion criterion:** the branch is one of {new, quick, review, upgrade} and the user has confirmed or corrected the default.

## New skill workflow

**Why this branch exists:** building the wrong skill is expensive. A structured design process prevents scope creep, hidden assumptions, and bloated drafts before any files are written.

The conductor walks through: clarify intent → classify → explore alternatives → design → curate scripts → assess global readiness → self-audit → confirm → draft → validate. See the detailed phases in [references/BRANCH_WORKFLOWS.md](references/BRANCH_WORKFLOWS.md).

**Completion criterion:** a final review report exists and the user has chosen to iterate or close.

## Quick skill workflow

**Why this branch exists:** a minimal skill still needs a clear problem, a sound shape, and a fundamentals check, even when deep design is skipped.

A compressed version of the New workflow. See the detailed phases in [references/BRANCH_WORKFLOWS.md](references/BRANCH_WORKFLOWS.md).

**Completion criterion:** a final review report exists and the user has chosen to iterate or close.

## Review workflow

**Why this branch exists:** skills drift. A periodic audit against the rubric keeps the skill library aligned with the fundamentals.

Read the existing skill, classify it, audit it against [references/AUDIT_RUBRIC.md](references/AUDIT_RUBRIC.md), and produce a structured report. See the detailed phases in [references/BRANCH_WORKFLOWS.md](references/BRANCH_WORKFLOWS.md).

**Completion criterion:** the audit report is complete, structured, and references the rubric criteria by id.

## Upgrade workflow

**Why this branch exists:** project-specific skills are useful, but making one global requires a precise inventory of assumptions and a confirmed remediation plan.

Read the existing skill, identify project-specific assumptions and missing dependency declarations, propose concrete remediation steps with effort estimates, and apply changes only after explicit approval. See the detailed phases in [references/BRANCH_WORKFLOWS.md](references/BRANCH_WORKFLOWS.md).

**Completion criterion:** a remediation plan exists and the user has approved or declined each proposed change.

## State and artifacts

The skill maintains working state so it can survive context compaction and resume later. All artifact paths are relative to the **detected** context directory. See [references/STATE_SCHEMA.md](references/STATE_SCHEMA.md) for frontmatter and body schemas.

| Artifact | Location | Purpose |
|---|---|---|
| Intent note | `{context}/skill-design/{skill-name}-intent.md` | Captured user intent and constraints. |
| Design draft | `{context}/skill-design/{skill-name}-design.md` | Structured skill design. |
| Alternatives report | `{context}/skill-design/{skill-name}-alternatives.md` | Existing options and recommendation. |
| Scripts plan | `{context}/skill-design/{skill-name}-scripts.md` | Proposed deterministic scripts. |
| Global readiness report | `{context}/skill-review/{skill-name}-global-readiness.md` | Blockers to global portability. |
| Self-audit | `{context}/skill-review/{skill-name}-self-audit.md` | Fundamentals check results. |
| Review report | `{context}/skill-review/{skill-name}-audit.md` | Guideline audit results. |
| Decision log | `{context}/skill-design/{skill-name}-decisions.md` | Record of decisions and rationale. |

Append decisions rather than overwriting them. Never overwrite an existing file without asking.

## Resumption logic

If the conversation is compacted, resume by reading the latest state files in this order:

1. Decision log.
2. Intent note.
3. Design draft or review report (whichever is most recent).
4. Latest self-audit or audit report.

Summarize completed work, pending work, current focus, and the recommended next action before continuing.

## User interaction rules

- **Confirm before any destructive action.** Drafting files, overwriting config, or modifying existing skills requires explicit approval.
- **In an untrusted project, prefer read-only inspection.** Confirm before reading skill files from a project you do not trust.
- **Ask one question at a time** when the answer shapes later decisions.
- **Present recommendations, not just options.** Propose a default and explain why.
- **Be explicit about assumptions and blockers.** Do not proceed on a guess about user intent.
- **Pair every negation with a positive directive.** For example: *Confirm the design before drafting; do not draft until the design is confirmed.*
- **Block on principle violations.** Explain the principle, why it matters, and offer a concrete alternative.
- **Warn on preference choices.** Explain the trade-off and recommend a default.
- **Ask when detection is ambiguous.** Present detected options and let the user choose.

## References

- [Audit rubric](references/AUDIT_RUBRIC.md)
- [Branch workflows](references/BRANCH_WORKFLOWS.md)
- [Pluggability and detection](references/PLUGGABILITY.md)
- [Dependencies and required capabilities](references/DEPENDENCIES.md)
- [State and artifact schemas](references/STATE_SCHEMA.md)
- [Context report schemas](references/CONTEXT_REPORTS.md)
- [Self-audit checklist](references/SELF_AUDIT_CHECKLIST.md)
- [Worker return contract](references/WORKER_CONTRACT.md)
- [Glossary](references/GLOSSARY.md)
- [Script curation guidance](references/GUIDE_SCRIPT_CURATION.md)
- [Skill examples](references/GUIDE_EXAMPLES.md)
- [Evaluation and testing](references/EVAL.md)
- [Maintenance and versioning](references/MAINTENANCE.md)
