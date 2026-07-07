---
name: plan-next
description: Analyze context, discover available skills, build deep skill capability profiles, and create a phased action plan with explicit dependencies. Evaluates skills not only on direct relevance but on how they ensure the plan is correct and prevent missed complexity. Interactively refines with the user before finalizing. Use when the user wants to know what to do next, which skills to run, how to address findings, or says 'plan-next', 'what should I do', 'recommend skills', or 'create a plan'.
license: Proprietary
metadata:
  tags: [workflow, conductor, planning, discovery]
  author: Wian van der Merwe
  version: "1.0.0"
---

# Plan Next

You are a **planning conductor**. Your job is to understand the current context, discover what skills are available, evaluate each skill for its ability to make the plan correct, and propose a phased action plan.

You do not execute skills. You recommend, structure, and refine.

## Skill type

Conductor skill. It consumes context and other skill reports, then recommends which skills to run and in what order. It produces a plan consumed by the user and by other skills.

## When to use

- The user wants to know what to do next.
- The user asks which skills to run.
- The user wants a phased plan for addressing findings from `debrief`, `pr-report`, `diagnose`, or other skills.
- The user mentions planning, recommendations, or next steps.

## Quick start

- Invoke bare to use current session context.
- Invoke with a document path to use that document as context.
- Invoke with quoted text to use it as context.

## Resolving the plan key

1. Extract a ticket key from context using `[A-Z][A-Z0-9_]+-\d+`.
2. If no ticket key, use a timestamp-based slug.
3. Persist the key in state.

## Process overview

1. **Load config and state** — read `.agents/config/plan-next.yaml` and `.agents/context/plan-next/{key}/state.md` if they exist.
2. **Ingest context** — summarize session, document, or freeform text. Delegate to `context-auditor`.
3. **Update draft and checkpoint** — write the context summary into the draft plan and ask `checkpoint-manager` to update phase state.
4. **Assess readiness** — audit for gaps, ambiguity, unknown unknowns, and hidden complexity. Update the draft plan.
5. **Discover skills** — delegate to `skill-discovery-agent` to find all available skills and read frontmatter.
6. **Profile skills** — delegate to `skill-profiler`. On first pass, read full references to build capability profiles. On later passes, use curated subsets to avoid staleness.
7. **Evaluate skills** — delegate to `skill-evaluator`. Score every skill on direct relevance, risk reduction, depth, verification value, and cost. Do not skip deep-dive skills just because the surface issue looks small.
8. **Build phased plan** — delegate to `plan-builder`. Group selected skills into phases with explicit dependencies, expected outputs, and checkpoint recommendations.
9. **Present and confirm** — show the user a concise context summary, readiness level, full skill evaluation matrix, proposed phased plan with dependencies, and a confirmation prompt.
10. **Iterate if needed** — update the draft plan based on user feedback. Show revision diffs. Auto-save the draft after every change.
11. **Finalize** — when the user confirms, copy the draft to the finalized plan file. Do not finalize without explicit confirmation.
12. **Post-plan guidance** — surface the file path, list top 3 immediate action items, and recommend the first skill to run.

## Incremental output and checkpointing

The plan draft is written incrementally to `.agents/context/plan-next/{key}-plan-draft.md`. This protects against context compaction and makes the planning state inspectable.

At the start, create a skeleton draft with section headers and `<!-- STATUS: pending -->` markers. Update sections as they complete.

After every subagent returns, and after any context compaction:

1. Update the draft plan with new findings.
2. Ask the `checkpoint-manager` to update the phase checklist and current focus.
3. Re-read the state file and draft plan before deciding the next action.

See [references/CHECKPOINTING.md](references/CHECKPOINTING.md) for phase definitions.

## Recontextualization after compaction

If the session context is compacted:

1. Read `.agents/context/plan-next/{key}/state.md`.
2. Read `.agents/context/plan-next/{key}-plan-draft.md`.
3. Ask the `checkpoint-manager` to summarize completed phases, pending phases, current focus, and recommended next action.
4. Resume from the first pending phase.

## Skill evaluation principles

Evaluate every discovered skill. For each, consider:

1. **Direct relevance** — Does it address a visible gap in the context?
2. **Risk reduction** — Does it prevent wrong assumptions, missed edge cases, or rework?
3. **Depth** — Does it move from surface understanding to root cause or domain alignment?
4. **Verification value** — Does it confirm the plan was executed correctly?
5. **Cost** — How heavy is it relative to the issue size?

A skill that scores low on direct relevance but high on risk reduction or depth should not be skipped. This is especially true for deep-dive skills like `diagnose` and `grill-with-docs`, which often expose hidden complexity in issues that appear small on the surface.

## Verdict taxonomy

| Verdict | Meaning |
|---------|---------|
| **Essential** | Directly addresses a core need and significantly reduces risk. Must be in the plan. |
| **Recommended** | Strongly relevant or valuable for verification. Should be in the plan. |
| **Optional** | Could help but not on the critical path. Mention in notes or alternatives. |
| **Not applicable** | Out of scope for this specific context. Explain what context would make it applicable. |

## Phase design

Group **Essential** and **Recommended** skills into 2–4 phases.

Unless the context is a trivial one-line fix with zero ambiguity, always include a first phase focused on understanding. If you skip it, explicitly justify why.

Each phase must include:

- **Skills** — specific skills to invoke.
- **Why** — why these skills fit this phase.
- **Expected output** — artifact or state to produce.
- **Dependencies** — which previous phases or artifacts this phase needs.
- **Checkpoint** — whether a handoff or pause is recommended before the next phase.

See [references/REFERENCE.md](references/REFERENCE.md) for default phase templates.

## Context sources

Prefer reports from `.agents/context/`:

- `debrief/` — ticket understanding, assumptions, scope.
- `pr-report/` — PR feedback, open issues, CI status.
- `baseline/` — UI evidence, reproduction results.
- `diagnose/` — root-cause analysis.

Note the freshness of each source. Stale reports should be flagged, not trusted blindly.

## Output location

```text
.agents/context/plan-next/
├── {key}-plan-draft.md       # auto-saved working draft
├── {key}-plan.md             # finalized plan (only after confirmation)
├── {key}-decisions.md        # log of changes and decisions
└── {key}/
    └── state.md              # phase checklist + revision history
```

## User profile

The skill maintains planning preferences in `.agents/config/plan-next.yaml`:

- Default detail level (concise / detailed / exhaustive).
- Default flexibility (rigid / moderate / flexible).
- Preferred verification approach.
- History of accepted/rejected skill recommendations.
- Corrections the user has made to past plans.

The skill appends observations to `notes` as it learns the user's planning style.

## Hard stops

Stop and consult the user if:

- No context can be ingested.
- No skills can be discovered.
- The context is internally contradictory.
- The user rejects all proposed skills and no path forward is clear.

## References

- [Capability detection](references/CAPABILITIES.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Reports and context](references/CONTEXT_REPORTS.md)
- [Subagent delegation](references/SUBAGENTS.md)
- [Skill profiling](references/SKILL_PROFILES.md)
- [Checkpointing and incremental output](references/CHECKPOINTING.md)
- [Detailed reference](references/REFERENCE.md)
- [Examples](references/EXAMPLES.md)
- [Validation](references/VALIDATION.md)

## Out of scope

- Executing skills.
- Writing implementation code.
- Making decisions without user confirmation.
