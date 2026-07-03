# Context reports

This skill produces and consumes reports stored in the detected context directory. Every report follows the standard schema below.

## Report header

```yaml
---
report: report-name
skill: skill-name
version: "1.0"
timestamp: ISO-8601
status: draft | final | stale | override
---
```

## Required sections

1. **Summary.** One-sentence verdict.
2. **Findings.** Structured observations or check results.
3. **Decisions made.** Any decisions captured during the work.
4. **Open questions.** Questions still pending.
5. **Blockers.** Issues that prevent progress.

## Freshness and missing reports

- Regenerate a report if the underlying skill files or version changed after the report timestamp.
- Never silently proceed if a required report is missing. Ask the user or regenerate it.
