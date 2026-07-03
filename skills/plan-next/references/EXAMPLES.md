# Examples

## Example skill evaluation matrix

| Skill | Verdict | Direct | Risk | Depth | Verify | Cost | Reasoning |
|-------|---------|--------|------|-------|--------|------|-----------|
| debrief | Essential | 5 | 5 | 5 | 2 | heavy | Ticket scope is unclear; debrief resolves ambiguities and documents assumptions. |
| diagnose | Recommended | 3 | 5 | 5 | 3 | heavy | Surface bug looks small but touches state management; diagnose prevents wrong fix. |
| grill-with-docs | Recommended | 2 | 4 | 5 | 2 | heavy | Domain terminology in ticket may be inconsistent with codebase. |
| baseline | Optional | 4 | 2 | 1 | 4 | medium | UI changed; baseline verifies, but no visual ambiguity reported. |
| verify-branch | Essential | 2 | 4 | 1 | 5 | light | Must verify branch before PR. |
| prototype | Not applicable | 1 | 1 | 2 | 1 | heavy | Design is already clear from ticket; no need to prototype. |

## Example phased plan

```markdown
## Phase 1: Understand
- **Skills:** debrief, diagnose
- **Why:** Ticket scope is ambiguous and the bug touches state management.
- **Expected output:** Debrief report + root-cause diagnosis.
- **Depends on:** none
- **Checkpoint:** `/handoff OC-1234` after this phase

## Phase 2: Implement
- **Skills:** direct work
- **Why:** Once root cause and scope are confirmed, implement the fix.
- **Expected output:** Code changes + tests.
- **Depends on:** Phase 1 (root cause confirmed)
- **Checkpoint:** none

## Phase 3: Verify
- **Skills:** verify-branch, baseline
- **Why:** Confirm fix works and UI is correct.
- **Expected output:** Passing branch verification + baseline report.
- **Depends on:** Phase 2 (implementation complete)
- **Checkpoint:** none
```

## Example revision diff

```markdown
### Changes from revision 1
- Added `diagnose` to Phase 1 after user flagged state-management concern.
- Moved `baseline` from Optional to Phase 3.
- Removed `prototype` because design is clear.
```
