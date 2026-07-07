# Context Reports

Orchestrate produces and consumes reports in `.agents/context/`.

## Produced reports

| Report | Path | Purpose |
|--------|------|---------|
| State | `.agents/context/orchestrate/{key}/state.md` | Working memory for the conductor loop. |
| Plan | `.agents/context/orchestrate/{key}/plan.md` | Finalized implementation plan. |
| Decisions | `.agents/context/orchestrate/{key}/decisions.md` | Durable decision log. |
| Assumptions | `.agents/context/orchestrate/{key}/assumptions.md` | Assumption log. |
| Phase contract | `.agents/context/orchestrate/{key}/phase-{N}.md` | Narrow contract for phase N. |
| Runbook | `.agents/context/orchestrate/{key}/runbook.md` | Final execution summary. |
| Index | `.agents/context/orchestrate/{key}/index.md` | Artifact index for long-running tickets. |

## Consumed reports

| Report | Path | Producer |
|--------|------|----------|
| Debrief | `.agents/context/debrief/{key}*.md` | `debrief` |
| Baseline | `.agents/context/baseline/{key}*.md` | `baseline` |
| Diagnose | `.agents/context/diagnose/{key}*.md` | `diagnose` |
| PR report | `.agents/context/pr-report/{key}*.md` | `pr-report` |
| Plan-next | `.agents/context/plan-next/{key}*.md` | `plan-next` |
| Checkpoint | `.agents/context/handoff/{key}-checkpoint.md` | `handoff` |

## Freshness

Track when each report was last updated. Stale reports should be flagged, not trusted blindly. A report is stale if it predates a significant finding or if its source has changed.
