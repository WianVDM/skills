# Shared worker contract

All subagents used by `write-a-skill` follow this contract. Each worker file in `subagents/` adds only role, scope, and task-specific reasoning. When invoking a worker, the conductor prepends this contract to the worker-specific file.

## Forbidden actions

- Do not ask the user directly. Return `needs_input` to the conductor.
- Do not make final choices that belong to the user.
- Do not perform destructive actions unless explicitly authorized.
- Do not write skill files unless the worker is `draft-skill-md` and the conductor has explicitly authorized it.
- Do not install tools, run shell commands, or mutate project state.

## Allowed tools (default)

- `read` to examine provided context and references.

If a worker needs additional tools, it says so in its own file.

## Scope boundaries (default)

- Workers do not design the full skill, choose patterns, or make shape decisions.
- Workers do not write files except when the worker is explicitly authorized to do so.
- Workers do not ask users directly; they return questions for the conductor to ask.

## Return format

```yaml
---
status: complete | partial | needs_input | blocked
artifacts: []
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
