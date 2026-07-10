---
name: worker-contract
description: Provide the canonical worker/subagent return contract for conductors to embed in subagent prompts. Use when composing a worker, standardizing subagent output, or referencing the shared return format, forbidden actions, and scope boundaries.
version: 1.0.1
invocation: model-invoked

---

# worker-contract

## Purpose

Provide the canonical return contract, forbidden actions, default tool scope, and default scope boundaries that conductors embed in subagent prompts.

## Type

Vocabulary building block.

## In scope

- Define the standard worker return format.
- List default forbidden actions for subagents.
- List default allowed tools for subagents.
- Define default scope boundaries for subagents.
- Provide guidance on how a conductor overrides the defaults.

## Out of scope

- This skill does not run a subagent or orchestrate work; conductors own workflow coordination.
- It does not write project-specific worker logic; conductors add role and task-specific instructions.
- It does not replace a conductor's judgment about when to delegate.

## When to use

- A conductor is composing a subagent prompt and needs the standard contract.
- A skill author wants to align a worker's return format with the shared convention.
- A skill needs to reference the canonical forbidden actions, allowed tools, or scope boundaries.

## Standard return contract

Workers return structured results in this format:

```yaml
---
status: complete | partial | needs_input | blocked
artifacts:
  - path/to/artifact.md
---

## Summary
A concise statement of what the worker did and the key outcome.

## Findings
- ...

## Decisions made
- Decision: ... | Rationale: ...

## Open questions
- Question the conductor should ask the user, if any.

## Blockers
- External blocker preventing progress, if any.
```

A worker must not ask the user directly unless explicitly authorized. It returns `needs_input`, and the main skill owns the user interaction.

## Default forbidden actions

- Do not ask the user directly; return `needs_input` to the conductor instead.
- Do not make final choices that belong to the user; defer decisions to the conductor.
- Do not perform destructive actions unless explicitly authorized; otherwise stay read-only.
- Do not write files unless the worker is explicitly authorized to do so.
- Do not install tools, run shell commands, or mutate project state; use only the tools and capabilities listed in the worker prompt.

A conductor may add worker-specific forbidden actions in addition to these defaults.

## Default allowed tools

- `read` to examine provided context and references.

If a worker needs additional tools, the worker prompt says so explicitly.

## Default scope boundaries

- Workers do not design the full solution, choose patterns, or make shape decisions.
- Workers do not write files except when explicitly authorized to do so.
- Workers do not ask users directly; they return questions for the conductor to ask.

A conductor narrows or extends these boundaries per worker.

## Customizing the contract

A conductor may prepend this contract to a worker-specific prompt and add:

- Role and scope specific to the task.
- Additional allowed tools.
- Additional forbidden actions.
- Worker-specific completion criteria.

Keep worker prompts shorter than the parent skill. A worker prompt that copies the parent skill is a sign the split is wrong.

## Security

- The contract is read-only reference.
- Destructive actions are forbidden unless explicitly authorized.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `docs/skill-standards/patterns/conductor.md`
