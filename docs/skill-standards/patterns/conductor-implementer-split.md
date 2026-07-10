# Conductor/implementer split

The **conductor/implementer split** is a cross-cutting pattern that separates **reasoning and orchestration** from **execution**. A conductor skill decides what to do and delegates to an implementer worker or skill that does it.

This pattern is a **cross-cutting specialization** of the conductor pattern. It is useful when the reasoning layer needs to stay clean and high-level while the execution layer needs to be focused and mechanical.

---

## When to use the split

Use the conductor/implementer split when:

- The task requires judgment before action.
- The execution layer is large enough to dilute the reasoning layer's context.
- The same execution logic might be reused with different reasoning strategies.
- You want to pressure-test the plan before implementing it.

Do not use the split when:

- The task is small and sequential.
- The execution is tightly coupled to the reasoning and cannot be cleanly separated.
- The cost of context handoff exceeds the benefit.

---

## Roles

### Conductor

The conductor owns:

- Understanding the goal.
- Planning the approach.
- Choosing which tools or workers to use.
- Reviewing results.
- Deciding whether to proceed, iterate, or stop.

The conductor does not write the implementation code, edit files, or run tests directly. It delegates those to the implementer.

### Implementer

The implementer owns:

- Executing the plan produced by the conductor.
- Using tools to read, write, and test files.
- Returning structured results.
- Asking for clarification only when the plan is ambiguous.

The implementer does not re-plan or change the approach without returning to the conductor.

---

## Example

- A **planning conductor** produces a task brief, acceptance criteria, and a recommended implementation approach.
- An **implementation worker** reads the brief, executes the changes, and returns a status report with artifacts.
- The conductor reviews the artifacts and decides whether to refine, verify, or finish.

---

## Why the split helps

- **Context isolation.** The reasoning layer is not contaminated by the details of execution.
- **Reusability.** The same implementer can be used with different conductors.
- **Testability.** The conductor's plan can be evaluated independently of the implementer's execution.
- **Safety.** A plan can be reviewed before any files are changed.

---

## Common mistakes

- **Conductor does implementation.** If the conductor starts writing code or editing files, the split has collapsed.
- **Implementer re-plans.** The implementer should execute the given plan, not argue with it or rewrite it.
- **Too fine-grained splits.** Spawning an implementer for trivial tasks wastes context. The split should be used when the reasoning and execution layers genuinely need separation.
- **Weak handoff contract.** The plan must be specific enough that the implementer can act without guessing.

---

## Example: plan-and-implement

This example shows a conductor skill that plans a change and an implementer worker that executes it. The conductor owns reasoning and orchestration; the implementer owns execution.

### Structure

```text
plan-and-implement/
├── SKILL.md
├── README.md
├── references/
│   └── IMPLEMENTER_CONTRACT.md
└── subagents/
    └── implementer.md
```

### `SKILL.md` (conductor)

```markdown
---
name: plan-and-implement
version: 1.0.0
metadata:
  author: workflow-team
invocation: user-invoked
description: Plan a change and then delegate implementation to a focused worker. Use when a task requires judgment about approach before any files are changed.
---

# Plan and implement

Produce a plan for a change, then delegate execution to an implementer worker.

## In scope

- Understand the user's goal.
- Explore the codebase enough to choose a reasonable approach.
- Produce a plan with acceptance criteria and risks.
- Delegate implementation to the implementer worker.
- Review the result and decide whether to iterate or finish.

## Out of scope

- Do not edit files directly.
- Do not run tests directly.
- Do not re-plan inside the implementer.

## Steps

1. Ask clarifying questions until the goal is unambiguous.
2. Explore relevant files and produce a plan.
3. Write the plan and acceptance criteria to a report file.
4. Spawn the `implementer` worker with the plan.
5. Review the worker's return status and artifacts.
6. If the plan is not met, return to step 2 with a refined plan.

## Handoff contract

Pass to the implementer:

- The plan and acceptance criteria.
- The relevant files and context.
- A clear instruction: execute the plan, do not re-plan.

Expect in return:

- `status: complete | partial | blocked`
- Artifacts changed.
- A summary of what was done.
- Any blockers or deviations.
```

### `subagents/implementer.md` (worker)

```markdown
# Implementer

You are an implementer worker for the `plan-and-implement` conductor.

Your job: execute the plan you are given by reading, writing, and testing files.

## In scope

- Read the plan and relevant files.
- Make the changes described in the plan.
- Run the project's test command.
- Return a structured status report.

## Out of scope

- Do not re-plan or change the approach.
- Do not ask the user questions.
- Do not make changes beyond the plan.

## Return format

```yaml
---
status: complete | partial | blocked
artifacts:
  - path/to/changed/file
---

## Summary
...

## Blockers
...
```

### Why it works

- **Context isolation**: the conductor stays high-level while the implementer handles file details.
- **Reusability**: the same implementer can be used by different conductors.
- **Testability**: the plan can be reviewed before any files are changed.
- **Safety**: a weak handoff is detected when the implementer returns `blocked` or `partial`.

---

## Research basis

- The **conductor/implementer split** is drawn from the research on multi-agent coordination and the broader pattern of separating reasoning from execution. obra/superpowers and similar practitioner sources describe this split explicitly.
- The research synthesis identifies **multi-agent coordination** and **file-based handoffs** as key patterns for complex tasks.
- The split is our own specialization of the conductor pattern, designed to keep the reasoning layer high-level while the execution layer remains focused and mechanical.
- The benefits of context isolation, reusability, testability, and safety are our own synthesis, supported by the research on delegation and subagent boundaries.

---

## Related documents

- [`conductor.md`](./conductor.md) — the general conductor pattern.
- [`building-block.md`](./building-block.md) — narrow capabilities the conductor can consume.
- [`../reference/evaluation-framework.md`](../reference/evaluation-framework.md) — evaluating multi-agent and composition behavior.
