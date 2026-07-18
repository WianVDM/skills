# Checkpointing and Incremental Output

`merge-latest` checkpoints progress for large or complex merges.

## When checkpointing is active

Checkpointing is always used, but it is especially important when:

- Conflict count exceeds the deep analysis threshold.
- The merge spans many files.
- Semantic conflicts require user input.
- The merge validation is long-running.

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
| 9 | Merge validation | Validation result recorded |
| 10 | Report | Final report written |

## State file

The state file at `.agents/context/merge-latest/{target}/state.md` follows the [`checkpoint`](../../../../blocks/project/checkpoint/SKILL.md) state schema and is maintained through its `create`, `update`, `resume`, and `validate` operations. `merge-latest` supplies the phases above and:

- **Owner frontmatter**: `target`, `upstream`, `status`.
- **Owner sections**: Branch Inference, Conflicts, Resolutions, Build.

```markdown
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

1. Invoke `checkpoint/resume` on the state file.
2. Read the merge report if it exists.
3. Resume from the first pending phase.
4. Do not restart completed phases unless the user asks.
