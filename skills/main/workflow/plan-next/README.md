# plan-next

Analyze context, discover skills, and create a phased action plan.

## Purpose

This skill acts as a planning conductor. It reads the current context, discovers available skills, builds deep capability profiles for each skill, evaluates them on how well they ensure a correct plan, and proposes a phased plan with explicit dependencies. It refines interactively with the user before finalizing.

## When to use

- Decide what to do next given a ticket, PR, bug, or feature request.
- Choose which skills to run and in what order.
- Build a structured plan from findings produced by other skills.

## Directory layout

```
plan-next/
├── SKILL.md                        # main skill instructions
├── README.md                       # this file
├── references/
│   ├── REFERENCE.md                # readiness audit, evaluation matrix, plan template
│   ├── CONFIG_PATTERN.md           # user profile + preferences
│   ├── CAPABILITIES.md             # skill discovery and availability detection
│   ├── CONTEXT_REPORTS.md          # consumed and produced reports
│   ├── SUBAGENTS.md                # delegation patterns
│   ├── SKILL_PROFILES.md           # how to build deep skill capability profiles
│   ├── CHECKPOINTING.md            # state + draft/finalize flow
│   ├── EXAMPLES.md                 # example evaluations and plans
│   └── VALIDATION.md               # review checklist
└── subagents/
    ├── context-auditor.md          # summarize context + assess readiness
    ├── skill-discovery-agent.md    # discover available skills
    ├── skill-profiler.md           # build capability profiles from references
    ├── skill-evaluator.md          # score each skill
    ├── plan-builder.md             # group skills into phases
    └── checkpoint-manager.md       # track planning iterations and state
```

## Key conventions

- Plans live in `.agents/context/plan-next/`.
- Config and user profile live in `.agents/config/plan-next.yaml`.
- The draft plan is auto-saved; the finalized plan is created only after user confirmation.
- The skill consumes reports from `.agents/context/` (debrief, pr-report, baseline, diagnose).
- Every discovered skill is evaluated with reasoning.
- Deep-dive skills are not skipped just because the surface issue looks small.
- Phase dependencies are explicit in the proposed plan.
- Revision diffs are shown when the plan changes.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on intent and move detailed guidance into `references/`. Preserve existing user preferences by pre-populating first-run questions with previous defaults.
