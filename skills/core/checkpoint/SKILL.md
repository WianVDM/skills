---
name: checkpoint
description: "Maintain phase checklists, current focus, and resume state for long-running conductor skills. Use when a skill needs to survive context compaction, track progress across phases, or resume from a previous session."
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [state, resume, checkpoint, building-block]
  verification_level: declared
license: Proprietary
depends:
  - context-reports
---

# checkpoint

Maintain phase checklists, current focus, and resume state for long-running conductor skills. Provides reliable state management for any conductor that runs across multiple turns or needs to survive context compaction.

## Skill type

Building-block skill. It only reads, validates, and writes state. It does not conduct research, make decisions, or ask the user questions.

## When to use

A conductor skill should call `checkpoint`:

- At the start of a session, to check for existing state.
- After every significant sub-step, to update phase status and focus.
- After context compaction, to resume from the recorded state.
- Before exiting, to record the final state.

Load this skill when the user or another skill needs to:

- Survive context compaction and resume a long-running workflow.
- Track progress across caller-defined phases.
- Record the current focus and last completed action.
- Validate a checkpoint state file for consistency.

## In scope

- Read a state file from a caller-provided path.
- Create a new state file if one does not exist.
- Maintain a `## Phase Checklist` with pending, in-progress, and completed states.
- Update `## Current Focus` to reflect the next pending phase or action.
- Update `## Last Completed Action` after each sub-step.
- Append to `## Session History` with timestamp, action, and resulting focus.
- Prune and archive session history when it exceeds a configured row limit (default 20).
- Provide a `resume` operation that returns completed phases, pending phases, current focus, and the next pending phase derived from the checklist.
- Validate state file consistency and report corruption or mismatches.

## Out of scope

- Do not make phase decisions for the caller.
- Do not conduct research or form assumptions.
- Do not ask the user questions.
- Do not write report, debrief, or implementation content — only state metadata.
- Do not enforce a specific phase model on the caller; phases are caller-defined strings.

## State file schema

### Frontmatter

```yaml
---
skill: checkpoint
version: 1.0.0
state_schema: 1.0.0
owner: debrief
key: OC-4644
updated_at: 2026-07-07T10:00:00Z
---
```

| Field | Required | Description |
|---|---|---|
| `skill` | yes | Always `checkpoint`. |
| `version` | yes | Skill version that wrote the state. |
| `state_schema` | yes | Version of the state file schema, independent of the skill version. |
| `owner` | yes | Name of the conductor skill that owns this state (e.g., `debrief`, `debrief-all`). |
| `key` | yes | Stable identifier for the work item (e.g., ticket key). |
| `updated_at` | yes | ISO 8601 timestamp of the last update. |

### Body

```markdown
# Checkpoint State: OC-4644

## Phase Checklist
- [x] Phase 0: Bootstrap
- [x] Phase 1: Gather evidence
- [/] Phase 2: Build context graph
- [ ] Phase 3: Resolve ambiguities
- [ ] Phase 4: Baseline
- [ ] Phase 5: Synthesize and validate
- [ ] Phase 6: Present

## Current Focus
Build context graph for ticket OC-4644.

## Last Completed Action
Ticket researcher returned normalized ticket data and context graph.

## Session History
| # | Timestamp | Action | Focus After |
|---|-----------|--------|-------------|
| 1 | 2026-07-07T09:00:00Z | Bootstrap complete | Gather evidence |
| 2 | 2026-07-07T09:05:00Z | Ticket researcher returned | Build context graph |

## Owner Sections
<!-- The owner skill can add arbitrary sections below this marker. -->
```

### History pruning

When `## Session History` exceeds the configured row limit (default 20), the oldest rows are archived to `{state_path}.history.md` and removed from the active state file.

## Operations and contracts

### `create`

Create a new state file with an initial phase checklist.

| Input | Description |
|---|---|
| `state_path` | Where to write the state file. |
| `owner` | Conductor skill name. |
| `key` | Work item identifier. |
| `phases` | List of phase names to pre-populate the checklist. |
| `focus` | Optional initial focus. |
| `max_history_rows` | Optional history row limit (default 20). |
| `overwrite` | Optional. If `true`, overwrite an existing state file. Default `false`. |

| Output | Description |
|---|---|
| `state_path` | Confirmed path to the state file. |
| `status` | `complete` or `blocked`. |

### `update`

Update the state after a sub-step.

| Input | Description |
|---|---|
| `state_path` | Path to the state file. |
| `completed_phase` | Phase to mark completed (optional). |
| `in_progress_phase` | Phase to mark in-progress (optional). |
| `current_focus` | Updated focus string (optional). |
| `last_action` | Description of what just completed (optional). |
| `owner_sections` | Arbitrary markdown sections to preserve (optional). |
| `max_history_rows` | Optional history row limit (default 20). |

| Output | Description |
|---|---|
| `state_path` | Confirmed path. |
| `status` | `complete` or `blocked`. |
| `phase_checklist` | Updated checklist with phase status. |
| `current_focus` | Updated focus. |
| `next_pending_phase` | Next pending phase derived from the checklist (deterministic, not a recommendation). |

### `resume`

Return the current state without modifying it.

| Input | Description |
|---|---|
| `state_path` | Path to the state file. |

| Output | Description |
|---|---|
| `completed_phases` | List of completed phases. |
| `pending_phases` | List of pending phases. |
| `in_progress_phase` | Current in-progress phase, if any. |
| `current_focus` | Recorded focus. |
| `last_action` | Last completed action. |
| `next_pending_phase` | Next pending phase derived from the checklist (deterministic, not a recommendation). |
| `owner_sections` | Preserved owner sections. |

### `validate`

Check that the state file is well-formed and consistent.

If `update` or `resume` is called on a missing or corrupt state file and `create` was not requested, `checkpoint` fails closed and reports the error to the caller.

| Input | Description |
|---|---|
| `state_path` | Path to the state file. |

| Output | Description |
|---|---|
| `valid` | `true` or `false`. |
| `errors` | List of inconsistencies, if any. |

## Lazy loading

`checkpoint` is only invoked when a conductor needs it. The caller decides when to load state; `checkpoint` does not perform any eager initialization.

## Security and safety

- Only reads/writes the caller-provided `state_path`.
- Never overwrites silently. `create` returns `blocked` if the target file already exists, unless the caller passes `overwrite: true`.
- Archives history rather than deleting it.
- Does not execute code, run shells, or install tools.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Dependencies](references/DEPENDENCIES.md)
