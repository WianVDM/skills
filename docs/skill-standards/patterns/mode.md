# Mode pattern

A **mode** is a transient behavior switch that changes how the agent behaves for a session or a task, without loading a full skill. It is not a skill, but it is related enough that skill authors should understand it.

Modes are useful when the same agent needs to operate in different stances — for example, coding vs. asking, or reasoning vs. executing — but the stance is too lightweight to justify a dedicated skill.

---

## When to use a mode

Use a mode when:

- The behavior switch is temporary and user-driven.
- The change is broad and cross-cutting, not tied to one domain.
- A skill would be too narrow or too heavyweight.

Examples:

- Aider's `code`, `ask`, and `architect` modes.
- A transient "planning mode" that makes the agent reason before acting.
- A "minimal mode" that reduces commentary and tooling.

Do not use a mode when:

- The behavior is domain-specific and reusable. Use a skill instead.
- The behavior needs a clear trigger, contract, or output. Use a skill instead.
- The behavior needs to be composed with other skills. Use a skill or conductor instead.

---

## Mode vs. skill

| Mode | Skill |
|------|-------|
| Transient switch. | Reusable unit of guidance. |
| Usually user-driven. | Triggered by description or user name. |
| Broad, cross-cutting stance. | Narrow, domain-specific contract. |
| No `SKILL.md`. | Has a `SKILL.md`. |
| Examples: `code`, `ask`, `architect`. | Examples: `review-ui`, `ticket-research`. |

A mode changes *how* the agent works. A skill tells the agent *what* to do.

---

## Relationship to skills

A skill can recommend or expect a mode, but it cannot enforce a mode reliably across harnesses. If a behavior is essential to the skill, encode it in the skill itself rather than relying on a mode.

For example, a conductor skill might say "in this phase, reason before acting," but it should not assume a global reasoning mode is active. It should delegate to a reasoning worker or include the reasoning step explicitly.

---

## Example: planning mode

A **mode** is not a skill, so it does not have a `SKILL.md`. It is a transient, user-driven behavior switch. Below is an example mode description that a harness might load when the user asks to enter planning mode.

### `planning-mode.md` (or harness mode description)

```markdown
# Planning mode

In this mode, the agent reasons before acting. Do not write code, edit files, or run commands until a plan has been agreed upon.

## When to enter this mode

- The user asks to plan a change before implementing it.
- A conductor skill explicitly requests a planning phase.
- The task is large enough that approach judgment matters more than immediate action.

## Behavior while in planning mode

1. Ask clarifying questions until the goal is unambiguous.
2. Produce a plan with phases, acceptance criteria, and risks.
3. Wait for explicit user confirmation before leaving planning mode.

## Relationship to skills

A skill can *recommend* planning mode, but it must not *depend* on it. If the harness does not support modes, the skill should run its planning phase inline rather than failing.
```

### Why it works

- The mode is **broad and transient**: it changes the agent's stance for a session or task, not a domain workflow.
- It **does not duplicate skill content**: skills still own specific workflows and contracts.
- It is **fallback-safe**: a skill that recommends the mode must still work if the mode is unavailable.

---

## Research basis

- The **mode pattern** is drawn from the research on Aider's `code`/`ask`/`architect` modes and similar transient behavior switches in other agent tools.
- The distinction between **modes** and **skills** is our own design choice: modes are transient and broad; skills are reusable and domain-specific.
- The recommendation that skills should not rely on modes for essential behavior is our own, based on the portability goal: a skill should be self-contained enough to work even when the user's current mode is different.

---

## Related documents

- [`../fundamentals/types.md`](../fundamentals/types.md) — choosing the right skill type.
- [`discipline-skill.md`](./discipline-skill.md) — prescriptive guidance that can act like a mode but is a skill.
