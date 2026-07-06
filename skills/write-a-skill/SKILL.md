---
name: write-a-skill
description: Design partner for creating, reviewing, and updating skills that follow the skill standards.
version: 4.7.0
invocation: user-invoked
metadata:
  author: Wian van der Merwe
  tags: [skill-authoring, conductor, standards]
  verification_level: declared
---

# write-a-skill

## Purpose

Help the user produce a skill that satisfies the skill fundamentals and applies the right architecture patterns.

## In scope

- Creating new skills from scratch.
- Drafting minimal skills quickly from a brief description.
- Reviewing existing skills against the fundamentals, after first understanding their purpose, shape, scope, and token economy.
- Updating existing skills to align with the standards.
- Recommending the right shape (skill, script, MCP server, context file, or mode) when the user is unsure.
- Delegating detection, audit, and validation to standalone building-block skills.
- Writing context reports and, after explicit approval, skill files.

## Out of scope

- This skill does not write application code; it only produces skill files, references, and context reports.
- It does not install or modify skills without explicit user approval; confirm every install, overwrite, or update before applying it.
- It does not choose a solution on the user's behalf without first exploring alternatives; present options with a recommended default.
- It does not replace the user's judgment on whether a skill is needed; ask the user to confirm the design decision before drafting.

## Portability and invocation

- **Invocation mode:** user-invoked. This is a meta-design conversation and should not stay loaded during normal work.
- **Scope:** global. It must work in any project with any harness.
- **Pluggability:** the skill detects the project layout and always confirms before writing files. See [references/PLUGGABILITY.md](references/PLUGGABILITY.md).
- **No hardcoded project paths:** paths are resolved through detection or user confirmation. The only acceptable hardcoded strings are the detection rules themselves.
- **Self-contained:** the skill ships with condensed fundamentals in [references/FUNDAMENTALS.md](references/FUNDAMENTALS.md) and [references/PATTERN_HINTS.md](references/PATTERN_HINTS.md). It can optionally bootstrap the full standards from a public repository on first run.

## Branch entry

Classify the user's intent into one top-level branch. If the intent is unclear, ask one clarifying question with a proposed default.

| Branch | Trigger | Internal gate | Outcome |
|---|---|---|---|
| **create** | User wants to produce a new skill or is unsure what shape to build. | `full`, `quick`, or `decide` | A designed and audited new skill, or a recommendation report. |
| **change** | User wants to audit or refine an existing skill. | `review` or `update` | An audit report, or a remediation plan with optional changes. |

**Completion criterion:** the branch is one of {create, change} and the user has confirmed or corrected the default.

## Workflow

The conductor runs this 10-phase pipeline. Each phase has a completion criterion and a decision gate. Phases may be compressed for the `quick` gate and skipped for the `decide` gate.

| Phase | What happens | Completion criterion |
|---|---|---|
| 1. **Clarify intent and choose gate** | Classify the top-level branch; resolve the internal gate; ask one question at a time if unclear. | Branch is one of {create, change}, gate is resolved, and user confirmed. |
| 2. **Explore alternatives** | Use `list-available-skills` and `search-skills-registry` to see what exists. | Alternatives report exists; user knows whether to create, reuse, or install. |
| 3. **Decide shape** | Decide whether the answer is a new skill, an existing skill, a script, an MCP server, or a context file. | User confirms the chosen shape. |
| 4. **Define identity** | Name, description, invocation, author, tags. Version only if the user requires it or the skill will be shared/consumed. | Frontmatter skeleton exists and user confirmed. |
| 5. **Define scope** | In-scope, out-of-scope, branches, assumptions. | Scope boundaries are explicit and defensible. |
| 6. **Select patterns** | Apply fundamentals; suggest Layer 2 patterns. Decide if the skill is configurable and, if so, which shared and skill-specific keys it needs. | Pattern list and config declaration (if any) exist and user confirmed. |
| 7. **Draft artifacts** | Generate `SKILL.md`, optional `README.md`, `references/`, `subagents/`, `scripts/`, `assets/`, and `config.yaml` if the skill is configurable. | Draft files exist and are linked correctly. |
| 8. **Audit and validate** | Run `audit-skill` and `validate-skill-frontmatter`. | Audit report exists with no blocking failures. |
| 9. **Generate evals** | Run `run-trigger-evals` for model-invoked skills. | `evals/evals.json` exists or user declined. |
| 10. **Confirm and write** | Present the full plan; write files only after explicit approval. | User approved; files written; decision log updated. |

## Subagent prompts

Workers in `subagents/` are invoked by composing the canonical worker contract from the `worker-contract` skill with the `write-a-skill`-specific composition layer in `subagents/_TEMPLATE.md` and the role-specific instructions in the worker file. The template adds the common return format, forbidden actions, and default tool/scope boundaries used by this conductor; see `references/WORKER_CONTRACT.md` for the shared contract and addendum.

## Create branch

**Why this branch exists:** building the wrong skill is expensive, and a structured design process prevents scope creep, hidden assumptions, and bloated drafts before any files are written. The branch also handles the "what should I build?" question.

**Internal gates**

| Gate | Trigger | Outcome | Completion criterion |
|---|---|---|---|
| **full** | User wants a complete design from scratch. | Full design workflow + draft. | A final review report exists in `{context}/skill-design/{skill-name}-design.md` and the user has explicitly approved, requested changes, or closed the branch. |
| **quick** | User wants a minimal skill from a brief description. | Compressed design workflow + draft. | A final review report exists in `{context}/skill-design/{skill-name}-design.md` and the user has explicitly approved, requested changes, or closed the branch. |
| **decide** | User is unsure whether the answer should be a skill, script, MCP, context file, or existing skill. | Recommendation report; no files written. | A decision report exists and the user has confirmed or rejected the recommended next step, or asked for more options. |

For the full phase list per gate, including the `decide` gate delegation to `decide-skill-shape`, see [references/BRANCH_WORKFLOWS.md](references/BRANCH_WORKFLOWS.md).

## Change branch

**Why this branch exists:** Skills drift and accumulate bloat. The change branch audits an existing skill by applying the review principles from `docs/skill-standards/REVIEW_PRINCIPLES.md`, then produces a verdict-led report or incomplete report.

**Internal gates**

| Gate | Trigger | Outcome | Completion criterion |
|---|---|---|---|
| **review** | User wants to audit an existing skill without changing it. | Verdict-led audit report, or incomplete report. | The audit report is complete, includes a verdict supported by findings, and references the rubric criteria by id. |
| **update** | User wants to refine or polish an existing skill to follow the standards. | Verdict-led audit report → remediation plan → draft changes → confirm. | A verdict-led audit report exists, a remediation plan exists, and the user has approved or declined each proposed change. |

For the full phase list per gate, including the `change` branch delegation to `review-skill`, see [references/BRANCH_WORKFLOWS.md](references/BRANCH_WORKFLOWS.md).

## Initialization

On first run in a project, execute the bootstrap routine:

1. Detect project context with `detect-project-context` to locate the project root and the recommended config directory.
2. Load config from `{recommended_config_dir}/write-a-skill.yaml` or create defaults.
3. Validate required capabilities (read, write, search, run scripts, network if standards init is offered).
4. **Run dependency self-diagnostics.** Check whether each required and recommended skill from [references/DEPENDENCIES.md](references/DEPENDENCIES.md) is installed and loadable. Report `full`, `degraded`, or `blocked` per `docs/skill-standards/fundamentals/dependencies-and-bundling.md`. If `blocked`, stop and explain how to install the missing required skills. If `degraded`, explain the reduced capability and ask whether to proceed.
5. Locate the canonical skill standards:
   - Check `docs/skill-standards/` at the project root.
   - Check `.agents/skill-standards/` if present.
   - Check the `standards_path` configured in `write-a-skill.yaml`.
   - If none are found, offer to fetch the official standards into the default `docs/skill-standards/` directory (or the configured `standards_path`).
   - If the fetch fails or the user declines, fall back to embedded [references/FUNDAMENTALS.md](references/FUNDAMENTALS.md) and [references/PATTERN_HINTS.md](references/PATTERN_HINTS.md).
6. Ask the user to confirm detected paths, default registry list, and standards source.
7. Persist initial notes in the context directory.

If the project context cannot be detected, fail closed and explain what is missing.

## State and artifacts

All artifacts are written as context reports so the session can survive compaction and be resumed. For shared context-report conventions, see the `context-reports` skill. Paths are relative to the detected context directory.

| Artifact | Location | Purpose |
|---|---|---|
| Intent note | `{context}/skill-design/{skill-name}-intent.md` | Captured user intent, constraints, and chosen branch/gate. |
| Alternatives report | `{context}/skill-design/{skill-name}-alternatives.md` | Existing skills and third-party options found. |
| Design draft | `{context}/skill-design/{skill-name}-design.md` | Structured design: identity, scope, type, patterns, dependencies. |
| Self-audit report | `{context}/skill-review/{skill-name}-self-audit.md` | Fundamentals check results. |
| Decision log | `{context}/skill-design/{skill-name}-decisions.md` | Append-only record of decisions and rationale. |

Append decisions rather than overwriting them. Never overwrite an existing file without asking.

## Resumption logic

If the conversation is compacted, resume by reading the latest state files in this order:

1. Decision log.
2. Intent note.
3. Design draft or review report (whichever is most recent).
4. Latest self-audit or audit report.

Summarize completed work, pending work, current focus, and the recommended next action before continuing.

## User interaction rules

- **Ask one question at a time** when the answer shapes later decisions.
- **Present recommendations, not just options.** Propose a default and explain why.
- **Confirm before any destructive action.** Writing, overwriting, or installing requires explicit approval.
- **Pair every negation with a positive directive.** For example: *Confirm the design before drafting; do not draft until the design is confirmed.*
- **Block on principle violations.** Explain the principle, why it matters, and offer a concrete alternative.
- **Warn on preference choices.** Explain the trade-off and recommend a default.
- **Ask when detection is ambiguous.** Present detected options and let the user choose.
- **In an untrusted project, prefer read-only inspection.** Confirm before reading skill files from a project you do not trust.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md) for the classified dependency list and the taxonomy from `docs/skill-standards/fundamentals/dependencies-and-bundling.md`.

Required tools and binaries: `read`, `write`, `edit`, `bash`, `find` (or equivalent); Python 3.x for bundled scripts.

## References

- [Fundamentals (condensed)](references/FUNDAMENTALS.md)
- [Pattern hints (condensed)](references/PATTERN_HINTS.md)
- [Pluggability and detection](references/PLUGGABILITY.md)
- [Branch workflows](references/BRANCH_WORKFLOWS.md)
- [Worker return contract](references/WORKER_CONTRACT.md)
- [State and artifact schemas](references/STATE_SCHEMA.md)
