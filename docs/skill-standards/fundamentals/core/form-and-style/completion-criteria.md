# Completion criteria

Whenever a skill has steps, each step should end on a **completion criterion**: a checkable condition that tells the agent the step is done.

A strong criterion is:

- **Checkable** — can the agent tell done from not-done?
- **Exhaustive** — where it matters, does it demand all the work?

| Weak | Strong |
|------|--------|
| Understand the ticket. | The ticket key, summary, acceptance criteria, and current status are recorded in the ticket report. |
| Write tests. | A failing test exists for the first behavior, and it fails for the expected reason. |
| Capture current state. | The report contains the branch, commit, scope, method, and at least one artifact. |

A vague criterion invites **premature completion** — ending a step before it is genuinely done because the agent's attention slips toward being finished. The cure is to sharpen the criterion first. Only if the criterion is irreducibly fuzzy and you actually observe the rush should you hide the later steps by splitting the skill.

---

## Premature completion

**Premature completion** happens when visible **post-completion steps** pull the agent forward. The agent sees the next steps and rushes the current one. Two defenses:

1. Sharpen the completion criterion. This is local and cheap.
2. Hide the later steps by splitting the skill or delegating them. This works only when the later steps leave the agent's context entirely (a subagent dispatch or a user-invoked hand-off).

See [`../common-mistakes/workflow-mistakes.md`](../common-mistakes/workflow-mistakes.md) for premature completion as a failure mode.

---

## Legwork

**Legwork** is the work the agent does within a step without being told explicitly how to do it — reading files, exploring the code, testing assumptions. A demanding completion criterion raises legwork. A weak criterion lets it stay thin.

Legwork is never written as its own step. It is latent in the wording of the step and its completion criterion.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
