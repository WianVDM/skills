# Checkpointing and Incremental Output

Orchestrate writes state incrementally so that progress survives context compaction and is inspectable at any time.

## Skeleton first

At the start of a run, create a skeleton state file with each section marked `<!-- STATUS: pending -->`. Fill sections as they complete.

## Update cadence

Update the state file after:

- Every subagent return.
- Every skill invocation.
- Every confidence assessment.
- Every challenge gate.
- Every plan draft revision.
- Every phase completion.
- Every validation run.
- Any context compaction.

## Checkpoint manager duties

The checkpoint-manager subagent:

1. Tracks completed and pending phases.
2. Updates the phase checklist.
3. Records the current focus.
4. Links each checkpoint to the previous one.
5. Produces a compact resume summary after compaction.

## Checkpoint chain

Each checkpoint references the previous checkpoint in `previous_checkpoint`. If this is the first checkpoint, write `none`.

## Resume summary

After compaction, the checkpoint-manager should return:

- Completed phases.
- Pending phases.
- Current focus.
- Recommended next action.
- Any detected deviations from expected state.
