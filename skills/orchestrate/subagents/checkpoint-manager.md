# Checkpoint Manager

## Purpose

Maintain the orchestration state, checkpoints, and resume summaries.

## Inputs

- Ticket key.
- Current state.md and plan.md.
- Phase completion status.
- Validation results.

## Process

1. Update state.md with the latest phase status.
2. Create or update the checkpoint file.
3. Link the current checkpoint to the previous one.
4. After compaction, produce a resume summary.
5. At the end, append the final execution summary to runbook.md.

## Outputs

- Updated state.md.
- Checkpoint file path.
- Resume summary.
- Final execution summary.
