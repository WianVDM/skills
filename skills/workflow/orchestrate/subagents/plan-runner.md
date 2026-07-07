# Plan Runner

## Purpose

Run the planning skill and interpret its recommendations for the conductor.

## Inputs

- Ticket key.
- Current state.md.
- Available context reports.
- Config `preferred_challenge_skills` and other role categories.

## Process

1. Invoke the first available planning skill (e.g., `plan-next`).
2. Capture its full output and any produced plan files.
3. Extract:
   - Essential skills.
   - Recommended skills.
   - Optional skills.
   - Readiness level.
   - Gaps identified.
4. Recommend which recommendation to accept and why.

## Outputs

- Summary of planning skill output.
- Skill recommendations with rationale.
- Recommended next skill to run.
- Any new gaps to add to state.
