# Reports and Context

## Produced reports

### Draft plan

```text
.agents/context/plan-next/{key}-plan-draft.md
```

Working plan. Auto-saved whenever the plan changes. Not the finalized plan.

### Finalized plan

```text
.agents/context/plan-next/{key}-plan.md
```

Created only after user confirmation.

### Decisions log

```text
.agents/context/plan-next/{key}-decisions.md
```

Logs changes made to the plan during refinement and execution.

### State file

```text
.agents/context/plan-next/{key}/state.md
```

Tracks phase checklist, revision history, and finalization status.

## Consumed context

| Source | Location | Use |
|--------|----------|-----|
| Debrief report | `.agents/context/debrief/{key}-report.md` | Ticket scope, assumptions |
| PR report | `.agents/context/pr-report/{key}-report.md` | Feedback, open issues, CI |
| Baseline report | `.agents/context/baseline/{key}-report.md` | UI evidence |
| Diagnose report | `.agents/context/diagnose/{key}-report.md` | Root cause |

## Key placeholder

`{key}` is derived from the ticket key if available, otherwise a timestamp-based slug.
