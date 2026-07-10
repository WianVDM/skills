# Conductor example

A conductor skill that coordinates research, state capture, and planning for a ticket.

```text
ticket-planning/
├── SKILL.md
├── README.md
├── references/
│   ├── WORKFLOW.md
│   └── SUBAGENTS.md
└── subagents/
    └── investigator.md
```

## `SKILL.md`

```markdown
---
name: ticket-planning
version: 1.0.0
invocation: user-invoked
description: Plan implementation for a ticket by researching its scope, capturing current state, and producing a structured plan. Use when the user asks to "plan this ticket", "scope this work", or "prepare an implementation plan".
---

# Ticket planning

Research a ticket, capture the current codebase state, and produce a structured implementation plan.

## In scope

- Research the ticket to understand scope, acceptance criteria, and constraints.
- Capture the current state of the relevant branch or commit.
- Explore files likely to change.
- Produce a plan with acceptance criteria, risks, and recommended steps.

## Out of scope

- Do not write implementation code.
- Do not modify files.
- Do not ask the user questions that another skill can answer.

## Steps

1. Read the ticket key and branch from the user or context report.
2. Run `ticket-research` to produce `.agents/context/ticket-research/{key}.md`.
3. Run `baseline` to capture `.agents/context/state-capture/{key}-{branch}.md`.
4. Spawn the `investigator` worker with the ticket and state reports.
5. Integrate the worker's findings into a plan report.
6. Return the plan to the user.

## Delegation rules

- Research and state capture are done by building-block skills, not inline.
- Code exploration is delegated to the `investigator` worker.
- The conductor owns integration and final plan structure.

## Failure handling

- If the ticket report is missing, stop and ask whether to run `ticket-research`.
- If the state capture is missing, ask whether to run `baseline`.
- If the investigator returns `blocked`, report the blocker and stop.

## Output format

Write a plan report to `.agents/context/plan/{key}.md` using the context report schema.

## Dependencies

See `references/DEPENDENCIES.md`.
```

## Why it works

- **Phases are explicit:** research, capture, explore, plan.
- **Work is delegated:** building blocks and a worker do the narrow work.
- **State is externalized:** reports in `.agents/context/` survive context compaction.
- **The conductor owns decisions:** it chooses what to run and integrates results.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
