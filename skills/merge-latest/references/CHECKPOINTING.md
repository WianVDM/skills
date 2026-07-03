# Checkpointing and Incremental Output

`merge-latest` checkpoints progress for large or complex merges.

## When checkpointing is active

Checkpointing is always used, but it is especially important when:

- Conflict count exceeds the deep analysis threshold.
- The merge spans many files.
- Semantic conflicts require user input.
- The build validation is long-running.

## Phases

| Phase | Name | Output |
|-------|------|--------|
| 1 | Resolve branches | Target and upstream identified, inference recorded |
| 2 | Pre-flight checks | Hard stops cleared |
| 3 | Reconnaissance | Merge metadata and conflict preview in state |
| 4 | Backup | Backup ref recorded |
| 5 | Merge attempt | Merge in progress or conflicts identified |
| 6 | Conflict classification | Each conflict classified |
| 7 | Deep analysis (if triggered) | Analyst findings in report |
| 8 | Trivial resolution | Safe resolutions applied |
| 9 | Build validation | Build result recorded |
| 10 | Report | Final report written |

## State file

```markdown
---
skill: merge-latest
version: 1
target: OC-4964
upstream: OC-3626
status: in-progress
updated_at: 2026-06-26T08:00:00Z
---

# Merge State: OC-4964

## Phase Checklist
- [x] 1. Resolve branches
- [x] 2. Pre-flight checks
- [x] 3. Reconnaissance
- [x] 4. Backup
- [ ] 5. Merge attempt
- [ ] 6. Conflict classification
...

## Current Focus
Phase 5 — attempt merge.

## Branch Inference
| Branch | Inferred Base | Confidence | Confirmed By | Date |
|--------|---------------|------------|--------------|------|
| OC-4964 | OC-3626 | high | history | 2026-06-26 |

## Conflicts
| File | Classification | Status | Reason |
|------|----------------|--------|--------|

## Resolutions
| File | Reason |
|------|--------|

## Build
| Command | Result | Output |
|---------|--------|--------|
```

## Resume rules

1. Read state.
2. Read report if it exists.
3. Call `checkpoint-manager` for status summary.
4. Resume from first pending phase.
5. Do not restart completed phases unless the user asks.
