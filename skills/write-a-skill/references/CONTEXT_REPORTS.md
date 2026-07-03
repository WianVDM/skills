# Context report schemas

This skill produces and consumes reports that are stored in the context directory. Every report should be predictable, timestamped, and versioned so that consumers can judge freshness and trust.

## Report header

Every report must include this header:

```yaml
---
report: report-name                    # e.g., self-audit, audit, global-readiness
skill: skill-name                      # the skill being reviewed/designed
version: "1.0"                         # version of the skill being reviewed/designed
timestamp: ISO-8601                    # when the report was generated
status: draft | final | stale | override
---
```

## Required sections

Every report must contain:

1. **Summary.** One-sentence verdict or recommendation.
2. **Findings.** Structured observations, ratings, or check results.
3. **Decisions made.** Any decisions captured during the work.
4. **Open questions.** Questions still pending.
5. **Blockers.** Issues that prevent progress.

## Report types

| Report | Filename | Purpose |
|---|---|---|
| Self-audit | `{skill-name}-self-audit.md` | Pre-draft fundamentals check. |
| Audit | `{skill-name}-audit.md` | Review of an existing or drafted skill. |
| Global readiness | `{skill-name}-global-readiness.md` | Blockers to global portability. |

## Freshness rules

- A report is **fresh** if it exists and no underlying source files have changed since its timestamp.
- A report is **stale** if the source files changed or the skill version changed after the report was generated.
- A **stale** report should be regenerated unless the user explicitly accepts it.
- A missing required report should trigger regeneration or consultation with the user; never silently proceed without it.

## Missing report handling

If a workflow step requires a report that does not exist:

1. Check whether the report can be regenerated automatically.
2. If yes, regenerate it and note the regeneration in the decision log.
3. If no, ask the user whether to proceed, abort, or provide the missing report.
4. Never fabricate or silently ignore a missing required report.
