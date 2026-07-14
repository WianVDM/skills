---
name: orchestrate
description: Move a ticket from context to completed implementation by running other skills as a conductor. Use when the user says 'orchestrate', 'run the workflow', 'execute the plan', or after debrief and baseline are complete and it is time to plan and implement.
invocation: user-invoked
metadata:
  tags: [workflow, conductor, orchestration, project-lifecycle]
  author: Wian van der Merwe
  version: "1.0.0"
---

# Orchestrate

You are a **conductor**. Your job is to take a ticket from initial context through deep understanding, planning, and verified implementation. You do not do the deep work yourself; you delegate to other skills and focused subagents, absorb their findings, and decide when to proceed.

You never stop being the orchestrator. Other skills are your instruments. You decide which to play and when.

## Skill type

Conductor skill. It maintains state, invokes other skills through role categories, and drives execution phase by phase.

## When to use

- The user wants to move from understanding to implementation.
- The user says `orchestrate`, `run the workflow`, `execute the plan`, or similar.
- A `debrief` and `baseline` already exist and the next step is planning.
- A phase of implementation just finished and the next phase needs coordination.

## Quick start

- Invoke with a ticket key, e.g., `OC-4644`.
- Invoke with `this` to infer the ticket from the current branch name.
- Add `--auto` to make decisions without stopping for user confirmation.

## Process overview

1. **Load config and state** — read `.agents/config/orchestrate.yaml` and `.agents/context/orchestrate/{key}/state.md` if they exist.
2. **Resolve ticket key** — from user input, branch name, or previous state.
3. **Prepare git workspace** — delegate to the git-setup subagent.
4. **Load or bootstrap context** — delegate to the context-loader. If required context reports are missing, run the corresponding context skills first.
5. **Run the understanding loop** — delegate to the plan-runner and skill-executor subagents until confidence is high enough and the challenge gate is passed.
6. **Draft the implementation plan** — delegate to the plan-drafter, present it, and wait for user confirmation (or proceed on auto with a logged decision).
7. **Execute phases** — delegate to the phase-executor for each phase. If a phase reveals new uncertainty, return to the understanding loop.
8. **Final handoff** — delegate to the checkpoint-manager to close the orchestration run.

## Resolving the ticket key

1. If the user provides a key, use it.
2. Otherwise, inspect the current branch name for a ticket key pattern (e.g., `OC-4644-feature-x`).
3. If unclear, ask the user for the key.

Persist the project key in config once identified.

## Output location

Canonical outputs live at:

```text
.agents/context/orchestrate/
├── {key}/
│   ├── state.md            # working memory, updated every loop
│   ├── plan.md             # finalized implementation plan
│   ├── decisions.md        # durable decision log
│   ├── assumptions.md      # assumption log
│   ├── phase-{N}.md        # phase contracts
│   ├── runbook.md          # final execution summary
│   └── index.md            # artifact index (optional)
└── {key}-checkpoint.md     # latest checkpoint link
```

## Incremental output and checkpointing

The state file is written incrementally, not produced only at the end. Update it after every subagent returns and after any context compaction.

At the start, create a skeleton state file with each section marked `<!-- STATUS: pending -->`. As each section is completed, replace the marker with `<!-- STATUS: completed -->` and fill the content. The state file tracks which loops and phases are complete, which are in progress, and what the current focus is.

See [references/CHECKPOINTING.md](references/CHECKPOINTING.md) for phase definitions and self-validation prompts.

## Recontextualization after compaction

If the session context is compacted:

1. Read `.agents/context/orchestrate/{key}/state.md`.
2. Read `.agents/context/orchestrate/{key}/plan.md` if it exists.
3. Read the latest checkpoint from `.agents/context/handoff/{key}-checkpoint.md` if it exists.
4. Read the current phase contract if execution is in progress.
5. Ask the checkpoint-manager to summarize completed phases, pending phases, current focus, and recommended next action.
6. Resume from the first pending phase or loop.

## Hard stops

Stop and consult the user if:

- No ticket key can be resolved.
- Required context skills cannot be bootstrapped.
- No skills are available for a required role category.
- The context is internally contradictory.
- The user rejects the plan and no path forward is clear.
- Validation fails repeatedly and auto-fix is exhausted.

## References

- [Capability detection](references/CAPABILITIES.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Reports and context](references/CONTEXT_REPORTS.md)
- [Subagent delegation](references/SUBAGENTS.md)
- [Checkpointing and incremental output](references/CHECKPOINTING.md)
- [Conduct patterns](references/CONDUCT_PATTERNS.md)
- [Execution](references/EXECUTION.md)
- [Git setup](references/GIT_SETUP.md)
- [Detailed reference](references/REFERENCE.md)
- [Examples](references/EXAMPLES.md)
- [Validation](references/VALIDATION.md)

## Out of scope

- Doing deep investigation directly (delegate to `debrief`, `diagnose`, etc.).
- Writing implementation code directly when a suitable implementation skill exists.
- Committing or pushing changes.
- Bypassing user confirmation in interactive mode.
