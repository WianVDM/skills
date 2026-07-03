# Worker return contract

All subagents for this skill return structured results in this format. They must not ask the user directly; they return `needs_input` to the conductor.

## Header

```yaml
---
status: complete | partial | needs_input | blocked
artifacts:
  - path/to/artifact.md
---
```

## Body sections

```markdown
## Summary
What the worker did and the key outcome.

## Findings
- Finding one.
- Finding two.

## Decisions made
- Decision: ... | Rationale: ...

## Open questions
- Question the conductor should ask the user, if any.

## Blockers
- External blocker, if any.
```

## Rules

- Do not ask the user directly.
- Do not make final user choices.
- Do not perform destructive actions unless explicitly authorized.
- Cite sources when quoting files or standards.
