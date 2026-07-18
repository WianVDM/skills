# Checkpointing and Incremental Output

`plan-next` writes the draft plan incrementally and uses the state file to track revisions and finalization.

## Core principle

> The draft plan and state file are the source of truth. After every subagent call and after any context compaction, re-read these files and resume from the first pending phase.

## Phases

| Phase | Name | Output |
|-------|------|--------|
| 1 | Ingest context | Context summary + readiness level in draft |
| 2 | Discover skills | Skill catalog in state |
| 3 | Profile skills | Capability profiles in state |
| 4 | Evaluate skills | Full evaluation matrix in draft |
| 5 | Build phased plan | Proposed plan with dependencies in draft |
| 6 | Present and confirm | User feedback recorded in state |
| 7 | Finalize | Finalized plan file created |

## Skeleton draft plan

```markdown
---
skill: plan-next
version: 1.0.0
key: OC-1234
status: draft
updated_at: 2026-06-26T08:00:00Z
---

# Plan Draft: [title pending]

<!-- STATUS: pending --> ## Context Summary
<!-- STATUS: pending --> ## Readiness
<!-- STATUS: pending --> ## Skill Evaluation Matrix
<!-- STATUS: pending --> ## Proposed Phased Plan
<!-- STATUS: pending --> ## Action Items
<!-- STATUS: pending --> ## Notes
```

## State file

The state file at `.agents/context/plan-next/{key}/state.md` follows the [`checkpoint`](../../../../blocks/project/checkpoint/SKILL.md) state schema and is maintained through its `create`, `update`, `resume`, and `validate` operations. `plan-next` supplies the phases above and:

- **Owner frontmatter**: `status`, `revision`.
- **Owner sections**: Revision History, Skills Evaluated.

```markdown
## Revision History
| # | Timestamp | User Feedback | Main Change |
|---|-----------|---------------|-------------|
| 1 | ... | "more detailed" | Added file-level tasks |
| 2 | ... | "add diagnose" | Added diagnose to Phase 1 |

## Skills Evaluated
| Skill | Verdict | Reasoning |
|-------|---------|-----------|
```

## Resume rules

1. Invoke `checkpoint/resume` on the state file.
2. Read the draft plan.
3. Resume from the first pending phase.
4. Do not restart completed phases unless the user asks for a full replan.

## Finalization

When user confirms:

1. Copy draft to finalized plan.
2. Update state to `status: finalized`.
3. Log final decisions.
