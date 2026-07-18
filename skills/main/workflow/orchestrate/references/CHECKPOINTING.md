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

## State operations

State maintenance is delegated to the [`checkpoint`](../../../../blocks/project/checkpoint/SKILL.md) block:

1. `checkpoint/create` at run start with the orchestration phases.
2. `checkpoint/update` after every cadence event above: mark completed phases, record the current focus and last completed action.
3. `checkpoint/resume` after compaction for completed phases, pending phases, current focus, and the next pending phase.
4. `checkpoint/validate` before final handoff.

The state file follows the checkpoint schema with `owner: orchestrate`; orchestrate-specific sections (plan status, confidence history, open questions) live as owner sections.

## Checkpoint chain

The conductor writes a checkpoint file per phase boundary at `.agents/context/handoff/{key}-checkpoint.md`. Each checkpoint references the previous checkpoint in `previous_checkpoint`. If this is the first checkpoint, write `none`.

## Resume summary

After compaction, `checkpoint/resume` returns:

- Completed phases.
- Pending phases.
- Current focus.
- Next pending phase.
- Preserved owner sections.

The conductor checks the returned state for deviations from expected state before resuming.
