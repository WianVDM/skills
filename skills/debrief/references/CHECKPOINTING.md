# Checkpointing and Incremental Output

`debrief` is a long-running workflow. Context compaction is a real risk. The skill counters this by writing the debrief document incrementally and using the state file as a persistent resume anchor.

---

## Core principle

> The debrief document and state file are the source of truth. The agent's memory is secondary. After every subagent call and after any context compaction, re-read these files and resume from the first pending phase.

---

## Report and state paths

- Debrief document: `{project-root}/.agents/context/debrief/{key}-{slug}.md`
- State file: `{project-root}/.agents/context/debrief/{key}/state.md`

`{key}` is the resolved ticket key. `{slug}` is a short, stable suffix derived from the ticket summary.

---

## Phases

The debrief workflow is divided into eight phases:

| Phase | Name | Output |
|-------|------|--------|
| 1 | Resolve ticket key and load context | Project key resolved, config loaded |
| 2 | Fetch ticket + related data | Debrief sections: Metadata, Discussion Summary, Attachments, Related Tickets, Development Context |
| 3 | Build context graph | State: Context Graph populated |
| 4 | Identify ambiguities | State: Ambiguities list populated |
| 5 | Resolve ambiguities via code exploration | Debrief section: Codebase Evidence; State: Ambiguities updated |
| 6 | Challenge assumptions | Debrief section: Assumptions Resolved; State: Ambiguities updated |
| 7 | Run baseline | Debrief section: Baseline Status; State: Baseline Status updated |
| 8 | Synthesize final debrief | All sections marked complete, frontmatter updated |

Each phase is marked complete in the state file only after its output has been written to the debrief document.

---

## Skeleton debrief document

At the start of Phase 2, create the debrief document with all sections marked pending:

```markdown
---
skill: debrief
version: 3
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-06-26T08:00:00Z
updated_at: 2026-06-26T08:00:00Z
summary: "Auth guard race condition during token refresh."
status: In Progress
priority: High
debrief_status: in-progress
debrief_confidence: Red (0%)
baseline_status: pending
consumed_context: []
artifacts_dir: OC-4644
---

# Debrief: OC-4644 — [title pending]

<!-- STATUS: pending --> ## Overview
<!-- STATUS: pending --> ## Metadata
<!-- STATUS: pending --> ## Problem Statement
<!-- STATUS: pending --> ## Acceptance Criteria / Desired Outcome
<!-- STATUS: pending --> ## Discussion Summary
<!-- STATUS: pending --> ## Attachments Reviewed
<!-- STATUS: pending --> ## Related Tickets
<!-- STATUS: pending --> ## Development Context
<!-- STATUS: pending --> ## Validity Assessment
<!-- STATUS: pending --> ## Codebase Evidence
<!-- STATUS: pending --> ## Assumptions Resolved
<!-- STATUS: pending --> ## Assumptions Requiring Clarification
<!-- STATUS: pending --> ## Baseline Status
<!-- STATUS: pending --> ## Debrief Confidence
```

As sections are completed, replace `pending` with `completed` and fill the content.

---

## Self-validation prompts

Before moving from one phase to the next, answer these questions:

1. **Is the current phase complete?**
   - Have all required sections been written?
   - Have all required state entries been updated?

2. **Does the new information contradict anything already recorded?**
   - Do any previous assumptions need revision?
   - Do any completed sections need updating?

3. **What is the next phase, and what is its goal?**
   - State the goal clearly before delegating.

4. **Is the current focus still correct?**
   - If context compaction occurred, re-confirm the focus with the checkpoint manager.

---

## Checkpoint manager usage

The `checkpoint-manager` subagent is called in two situations:

### 1. After every subagent returns

Ask the checkpoint manager to:

- Read the current state file and debrief document.
- Mark the just-completed phase as complete.
- Update `Current Focus` and `Last Completed Action`.
- Identify the next pending phase.
- Return a concise status summary.

### 2. After context compaction

Ask the checkpoint manager to:

- Read the current state file and debrief document.
- Report completed phases, pending phases, current focus, and recommended next action.
- Do not proceed until the main agent has re-read the files.

---

## Resume rules

After context compaction:

1. Read `.agents/context/debrief/{key}/state.md`.
2. Read `.agents/context/debrief/{key}-{slug}.md`.
3. Call `checkpoint-manager` for a status summary.
4. Resume from the first unchecked phase in `## Phase Checklist`.
5. Do not restart completed phases unless new evidence contradicts them.
6. Update `Current Focus` before doing any work.

---

## Focus guardrails

If the agent finds itself doing work that does not serve the current `## Current Focus`:

1. Stop.
2. Re-read the state file.
3. Re-read the debrief document.
4. Call `checkpoint-manager` if unsure.
5. Resume from the documented focus.

---

## State history pruning

The `## Session History` table can grow large. When it exceeds 20 rows or the state file becomes unwieldy, archive the oldest rows to a separate history file (e.g., `.agents/context/debrief/{key}/state-history.md`) and keep only the most recent iterations in the active state file.

---

## Finalization

When all phases are complete:

1. Update `debrief_status` to `complete`.
2. Update `debrief_confidence` to final value.
3. Remove any remaining `pending` markers (all sections should be `completed`).
4. Ask `checkpoint-manager` to verify completeness and consistency.
5. Present findings to the user.
