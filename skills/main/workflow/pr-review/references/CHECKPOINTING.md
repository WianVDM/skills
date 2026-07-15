# Checkpointing

Incremental output and resume rules for `pr-review`.

## Output files

| File | Purpose |
|---|---|
| `{context_dir}/pr-review/{key}/state.md` | Current phase, tool selections, confidence, and decisions. |
| `{context_dir}/pr-review/{key}/{key}-review-draft.md` | Proposed review. |
| `{context_dir}/pr-review/{key}/{key}-review-payload.md` | Exact manual payload if posting is not used. |
| `{context_dir}/pr-review/{key}/{key}-decisions.md` | Append-only decision log. |

## Status markers

Use HTML comments in reports to mark section status:

```html
<!-- STATUS: pending -->
<!-- STATUS: in_progress -->
<!-- STATUS: completed -->
```

## Phase checklist in state.md

The state file contains a checklist of all phases. Mark each phase `complete` when done.

## Resume behavior

1. Read state.md on entry.
2. If the previous session stopped mid-phase, restart that phase from the beginning.
3. Re-run `tool-discovery` if the recorded preferred tool is no longer available.
4. Re-check `artifact-freshness` before reusing any prior report.
5. If context was compacted, re-read all observations from `chainlog` for the work item.

## Observation-first design

`pr-review` stores each capability's tool output in `chainlog` under the identity `{work_item_type}/{work_item_key}`. Reports are views over those observations. When resuming, query the chainlog instead of re-invoking tools if the observations are fresh.
