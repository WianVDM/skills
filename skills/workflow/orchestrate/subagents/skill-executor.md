# Skill Executor

## Purpose

Execute a skill by role category and capture its output for the conductor.

## Inputs

- Ticket key.
- Role category (e.g., `diagnose`, `challenge`, `implementation`, `verification`).
- Config mapping for that role category.
- Current state.md and context reports.

## Process

1. Resolve the role category to a concrete skill using config and capability detection.
2. If no skill is available, fall back to the generic subagent for that role.
3. Invoke the skill with the ticket key and relevant context.
4. Capture its output and any produced artifacts.
5. Summarize findings, confidence impact, and new gaps.

## Outputs

- Skill output summary.
- Artifacts produced or updated.
- Confidence impact.
- New gaps or contradictions.
- Recommended next action.
