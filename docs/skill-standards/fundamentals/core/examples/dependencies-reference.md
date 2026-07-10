# Dependencies reference

A `references/DEPENDENCIES.md` file makes a skill's dependencies explicit.

```markdown
# Dependencies

## Required skills

- `state-capture` — for capturing initial UI or system state.

## Consumed reports

- `.agents/context/state-capture/{key}.md`

## Required tools

- Access to the project's issue tracker.
- Ability to read source files and documentation.
```

## Why it works

- **Dependencies are explicit.** Nothing is hidden.
- **Skills and reports are separated.** Consumers know what skills produce the reports they need.
- **Capabilities are stated.** A maintainer can see what the skill expects from the environment.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
