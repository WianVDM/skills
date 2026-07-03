# Context Loader

## Purpose

Ensure all required context reports exist before the conductor loop begins. If a report is missing, bootstrap it by invoking the corresponding context skill.

## Inputs

- Ticket key.
- Config `required_context_skills`.
- Existing `.agents/context/` reports.

## Process

1. For each skill in `required_context_skills`:
   - Check whether a report exists in `.agents/context/{skill-name}/{key}*.md`.
   - If missing, invoke the skill and wait for it to produce a report.
   - If the skill fails, report failure to the conductor.
2. Read existing reports and summarize their contents.
3. Identify any missing optional context that would help planning.

## Outputs

- Summary of available context.
- List of bootstrapped reports.
- List of missing required reports (if any).
- Recommended next action.
