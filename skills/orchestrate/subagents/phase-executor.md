# Phase Executor

## Purpose

Execute one phase of the approved plan.

## Inputs

- Ticket key.
- Phase number and phase contract.
- Approved plan.md.
- Latest checkpoint.
- Current state.md, decisions.md, assumptions.md.

## Process

1. Recontextualize by reading all relevant artifacts.
2. Perform self-consistency check.
3. Generate or update the phase contract.
4. Execute checklist items sequentially.
5. Mark items complete.
6. Run verification skills.
7. Handle validation failure according to mode.
8. Run the checkpoint skill to create the next checkpoint.

## Outputs

- Completed checklist.
- Validation results.
- Checkpoint path.
- Any new gaps or contradictions.
- Recommended next action.
