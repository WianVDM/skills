# Conductor

A conductor skill coordinates other skills, scripts, subagents, or tools through a multi-phase process to reach a larger goal. It does not do the deep work itself; it delegates.

Conductors are the composition layer of the architecture. They turn building blocks into workflows, integrate findings from workers, maintain state across phases, and decide what to do next.

---

## When to use a conductor

Use a conductor when:

- The work is too large or cross-cutting for one building block.
- Sequencing matters and the agent would otherwise skip phases.
- State must be maintained across invocations or context compactions.
- Multiple building blocks must be composed into a larger workflow.
- The workflow requires judgment about which tools to invoke and when.

Do not use a conductor when:

- The task is a single narrow capability that fits in one building block.
- The only value is presentation or confirmation; use a wrapper instead.
- The task is better handled by a simple sequence of steps in one skill.

---

## Composition over monoliths

A conductor turns building blocks into workflows. It does not replace them. If a conductor starts doing the narrow work itself, it has become a monolith. Split the narrow work back into a building block and let the conductor orchestrate.

---

## Core responsibilities

A conductor is responsible for:

1. **Defining the workflow** — what phases exist, in what order, and what each phase produces.
2. **Delegating work** — sending focused tasks to subagents, workers, or building-block skills.
3. **Maintaining state** — tracking progress across phases and surviving context compaction.
4. **Collecting and sharing observations** — appending tool outputs to a [`chainlog`](./chainlog.md) when the data may be reused across skills or runs.
5. **Integrating findings** — combining worker outputs before deciding what to do next.
6. **Handling failure** — deciding whether to retry, escalate, or stop when a step fails.
7. **Owning user interaction** — or delegating it to a wrapper so the workflow stays clean.

---

## Conductor anatomy

```
conductor-name/
├── SKILL.md                 # workflow, phases, delegation rules
├── README.md                # for human maintainers
├── references/
│   ├── WORKFLOW.md          # detailed phase definitions
│   ├── SUBAGENTS.md         # worker contracts
│   └── CONTEXT_REPORTS.md   # schemas for reports this skill produces/consumes
├── subagents/               # worker personas
│   └── worker-name.md
├── scripts/                 # deterministic helpers
│   └── detect-env.py
└── assets/                  # templates for reports
    └── templates/
```

A conductor is usually **user-invoked** because it runs a meaningful workflow on behalf of the user. It may be **model-invoked** when the agent must autonomously coordinate a recurring multi-step process.

---

## Delegation

Delegation lets a conductor stay focused on decisions while handing focused work to subagents or other skills. It prevents context bloat and keeps the main skill in a conductor role.

### When to delegate

Delegate when:

- The sub-task is large enough to dilute the main skill's context.
- The sub-task has a different focus than the main skill.
- The sub-task can return a clean artifact or finding.
- The main skill should remain a conductor or reviewer.
- The sub-task benefits from a fresh context or a specialized persona.

Examples:

- A conductor skill delegates research to a `ticket-researcher` worker.
- A review skill delegates standards checking and spec checking to two parallel workers.
- A planning skill delegates environment detection to a helper script.

### When not to delegate

Do not delegate when:

- The task is small and sequential.
- The cost of context handoff exceeds the benefit.
- The sub-task requires ongoing user collaboration that the main skill should own.
- The sub-task is so tightly coupled to the main skill that splitting adds no clarity.

A skill should not try to do everything itself, but it also should not spawn workers for trivial work.

---

## Worker personas

Define workers in `subagents/`. Each worker prompt must state:

- Role and scope.
- What it should do.
- What tools or capabilities it may use.
- What it must not do.
- What format to return.

A worker does not need the full skill philosophy. It needs:

- The specific task.
- The boundaries.
- The tools it may use.
- The return format.

Keep worker prompts shorter than the parent skill. A worker prompt that copies the parent skill is a sign the split is wrong.

---

## Standard return contract

Workers return structured results. Define the contract once and reference it from each worker prompt.

```markdown
---
status: complete | partial | needs_input | blocked
artifacts:
  - path/to/artifact.md
---

## Summary
...

## Findings
- ...

## Decisions made
- ...

## Open questions
- ...

## Blockers
- ...
```

A JSON Schema for the worker return frontmatter is maintained at `schemas/worker-return-contract.schema.json`.

A worker must not ask the user directly unless explicitly authorized. It returns `needs_input`, and the main skill owns the user interaction.

---

## Delegating to other skills

A skill can invoke another skill instead of a generic subagent. This is useful when:

- The sub-task is a complete domain that already has a skill.
- The sub-task needs the same standards and outputs every time.
- The producing skill's output is a report the main skill consumes.

When invoking another skill:

- Pass the required context clearly.
- Do not silently assume the skill exists; declare the dependency.
- Handle absence gracefully: consult the user or note the gap.

---

## Delegating to scripts

Use scripts for deterministic, repeatable logic. A skill should call a script when:

- The input and output are well-defined.
- No reasoning or judgment is required.
- The result is needed quickly and cheaply.

Scripts should be isolated, documented, safe, and failure-explicit. They should not ask the user for input; the skill should collect input and pass it as arguments or environment variables.

---

## The main skill as conductor

When a skill delegates heavily, its main job becomes:

1. Decide what needs to happen.
2. Choose the right worker or skill.
3. Pass the right context.
4. Integrate the results.
5. Decide whether to proceed, pause, or escalate.

The conductor does not do the deep work. It maintains state, tracks progress, and makes decisions.

---

## Anti-patterns

### Orchestrator that does the work

A conductor skill that investigates, writes code, and runs tests inline. It becomes too long and loses oversight.

### Worker without boundaries

A subagent prompt that says “help with this” without scope, tools, or return format. The worker will drift.

### Layered delegation for its own sake

Spawning workers for tasks that fit in one or two tool calls. The handoff cost exceeds the benefit.

### Silent dependency on a worker or skill

Assuming a subagent or skill exists without declaring it. When it is missing, the skill fails unpredictably.

---

## Research basis

- The **conductor** as a coordinator of other skills and tools is our own term, but the underlying pattern is widely supported by the research. obra/superpowers describes **subagent-driven development** and durable progress ledgers; Claude Code and Codex both provide native subagent primitives; the research synthesis identifies multi-skill coordination as a core need.
- The **conductor does not do the deep work** rule is our own design choice, supported by the research finding that monolithic skills tend to bloat context and lose oversight.
- The **standard worker return contract** is our own convention, but it aligns with the research emphasis on structured handoffs and predictable integration between workers and orchestrators.
- **Delegation heuristics** (when to delegate, when not to) are our own practice, informed by the trade-off between context handoff cost and the benefit of fresh, focused worker context.
- The **stateful, multi-phase workflow** role of conductors is supported by the research on context compaction and the need to survive long-running tasks across sessions.

