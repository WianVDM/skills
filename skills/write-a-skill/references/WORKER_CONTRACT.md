# Worker return contract

All subagents used by `write-a-skill` must return a structured result in this format. They must not ask the user questions directly; instead, they return `needs_input` with the questions the conductor should ask.

## Header

```yaml
---
status: complete | partial | needs_input | blocked
artifacts:
  - path/to/artifact.md
---
```

- **complete:** the worker finished its task and produced the expected artifacts.
- **partial:** the worker made progress but needs additional information or action to finish.
- **needs_input:** the worker needs the conductor to ask the user one or more questions.
- **blocked:** the worker cannot proceed due to an external blocker.

## Body sections

```markdown
## Summary
A concise statement of what the worker did and the key outcome.

## Findings
- Finding one.
- Finding two.

## Decisions made
- Decision: ... | Rationale: ...

## Open questions
- Question the conductor should ask the user, if any.

## Blockers
- External blocker preventing progress, if any.
```

## Rules for workers

- **Do not ask the user directly.** Return `needs_input` with clear questions for the conductor.
- **Do not make final choices.** Propose options and defaults; let the user confirm through the conductor.
- **Do not write skill files unless explicitly asked.** The `skill-drafter` is the only worker that writes final skill files.
- **Do not perform destructive actions.** No deleting, overwriting, or shell commands that mutate state.
- **Be specific about tools.** Name the exact tools used (e.g., `read`, `bash`, `find`, `web_search`).
- **Cite sources.** When quoting a file or standard, name the file or reference.
- **Fail closed.** If a required capability is missing, report `blocked` with a clear explanation.
