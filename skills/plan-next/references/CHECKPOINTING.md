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

```markdown
---
skill: plan-next
version: 1.0.0
key: OC-1234
status: awaiting-confirmation
revision: 2
updated_at: 2026-06-26T08:00:00Z
---

# Plan State: OC-1234

## Phase Checklist
- [x] 1. Ingest context
- [x] 2. Discover skills
- [x] 3. Profile skills
- [x] 4. Evaluate skills
- [x] 5. Build phased plan
- [ ] 6. Present and confirm
- [ ] 7. Finalize

## Current Focus
Phase 6 — present plan to user and collect feedback.

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

1. Read state.
2. Read draft plan.
3. Call `checkpoint-manager` for status summary.
4. Resume from first pending phase.
5. Do not restart completed phases unless user asks for a full replan.

## Finalization

When user confirms:

1. Copy draft to finalized plan.
2. Update state to `status: finalized`.
3. Log final decisions.
