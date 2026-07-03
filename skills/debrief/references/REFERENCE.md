# Debrief Reference

Research checklist, state management, context graph, ambiguity resolution, and output generation for `debrief`.

---

## Research checklist

Gather everything available from the configured issue tracker and related sources.

- [ ] **Core ticket** — summary, description, status, priority, assignee, reporter, created/updated dates, labels, components, fix versions.
- [ ] **Acceptance criteria** — explicit or inferred.
- [ ] **Comments** — read chronologically. Note decisions, scope changes, blockers, clarifications.
- [ ] **Attachments** — summarize images, logs, documents.
- [ ] **History** — status transitions, time in status, stalls or back-and-forth.
- [ ] **Development info** — linked PRs, branches, commits.
- [ ] **Related tickets** — parent, subtasks, linked issues, duplicates. Search for context if description suggests a duplicate.
- [ ] **Worklog** — optional; may reveal effort already spent.
- [ ] **Active PRs** — open PRs linked to the ticket or related area.

---

## Delta mode / reuse existing debrief

Before starting full research, check for existing artifacts:

1. **Check state file** — `.agents/context/debrief/{key}/state.md`
   - If exists → read it. Resume from `## Phase Checklist` and `## Current Focus`.

2. **Check debrief document** — `.agents/context/debrief/{key}-{slug}.md`
   - If exists and `generated_at` is recent (e.g., <24h) → read it as starting context.
   - Skip re-fetching ticket details unless the user asks for a refresh.
   - Skip re-scanning attachments unless something changed.
   - Re-resolve ambiguities with current codebase state.
   - Update the document in place rather than regenerating from scratch.

3. **If no existing debrief** → proceed with full research.

---

## Incremental writing

The debrief document is built section by section. Use status markers to track progress:

```markdown
<!-- STATUS: pending --> ## Overview
<!-- STATUS: completed --> ## Metadata
...
```

When a section is complete:

1. Replace `pending` with `completed`.
2. Add the section content below the marker.
3. Update `updated_at` in the frontmatter.
4. Ask the checkpoint manager to update the phase checklist.

This allows the agent to resume after context compaction without re-doing completed work.

---

## State file specification

Path: `.agents/context/debrief/{key}/state.md`

This is the investigator's working memory and the anchor for resuming after context compaction. Read it at the start of every iteration. Write to it before and after every subagent call.

```markdown
---
skill: debrief
version: 3
ticket: OC-4644
updated_at: 2026-06-26T08:42:00Z
---

# Debrief State: OC-4644

## Phase Checklist
- [x] Phase 1: Resolve ticket key and load context
- [x] Phase 2: Fetch ticket + related data
- [x] Phase 3: Build context graph
- [ ] Phase 4: Identify ambiguities
- [ ] Phase 5: Resolve ambiguities via code exploration
- [ ] Phase 6: Challenge assumptions
- [ ] Phase 7: Run baseline
- [ ] Phase 8: Synthesize final debrief

## Current Focus
Identifying ambiguities in ticket OC-4644.

## Last Completed Action
Ticket researcher returned normalized ticket data and context graph.

## Session History
| # | Timestamp | Action | Confidence After |
|---|-----------|--------|------------------|
| 1 | {iso} | Initial research, 3 ambiguities found | Yellow (65%) |
| 2 | {iso} | Resolved auth guard ambiguity | Green (88%) |

## Context Graph
| Source | Key | Relevance | Contribution | Timestamp |
|--------|-----|-----------|--------------|-----------|
| Core ticket | OC-4644 | High | Auth guard race condition | {iso} |
| Related ticket | OC-1234 | Medium | Similar timing issue | {iso} |
| Codebase | auth.guard.ts | High | Confirms role-based flow | {iso} |
| Baseline | OC-4644 | High | Bug reproducible | {iso} |

## Ambiguities
| Ambiguity | Status | Confidence | Resolution | Basis | Iteration |
|-----------|--------|------------|------------|-------|-----------|
| Which guard handles this? | resolved | High (85%) | `auth.guard.ts` | Ticket + code | 1 |
| Validation timing | escalated | Low (40%) | — | Ticket contradicts itself | 1 |

## Codebase Explored
| File | Why Searched | Key Finding | Iteration |
|------|--------------|-------------|-----------|
| `src/app/guards/auth.guard.ts` | Resolve ambiguity | Uses `canActivate` with role check | 1 |
| `src/app/billing/billing.service.ts` | Similar feature pattern | Comparable validation approach | 1 |

## Baseline Status
| Status | Notes | User Override | Timestamp |
|--------|-------|---------------|-----------|
| Complete | 3 screenshots captured | — | {iso} |

## Ticket Context Cached
- Summary: {cached}
- Acceptance criteria: {cached}
- Last fetch: {iso}

## Next Action
{what the next debrief iteration should do}
```

### Section rules

- **Phase Checklist:** Update after every subagent returns. This is the primary resume anchor.
- **Current Focus:** Update whenever the agent switches tasks. Be specific.
- **Last Completed Action:** Record what just finished and what it produced.
- **Session History:** Append only. Every iteration gets a row. Archive old rows when the table grows large.
- **Context Graph:** Add every source of evidence with relevance and contribution.
- **Ambiguities:** Update status on each iteration. Do not delete rows.
- **Codebase Explored:** Append only. Re-explore only if the ambiguity changed.
- **Baseline Status:** Update after each baseline attempt.
- **Ticket Context Cached:** Update when fresh tracker data is fetched.
- **Next Action:** Update before delegating the next task.

---

## Codebase evidence

When exploring the codebase to resolve ambiguities, record findings in a dedicated section of the debrief document.

**What to capture:**

- Files that contain relevant logic.
- Patterns that suggest expected behavior.
- Similar features that can be used as reference.
- Files that will likely need modification.

**Format:**

```markdown
## Codebase Evidence
| File | Relevance | What It Shows |
|------|-----------|---------------|
| `src/app/guards/auth.guard.ts` | High | Current role-based auth flow |
| `src/app/billing/billing.service.ts` | Medium | Comparable validation pattern |
```

---

## Debrief confidence

Rate overall confidence in the entire debrief after ambiguity resolution and challenging.

| Level | Range | Meaning | Action |
|-------|-------|---------|--------|
| **Red** | 0-59% | Too many unresolved ambiguities or contradictions. | Stop. Present escalated items to user. |
| **Yellow** | 60-84% | Some assumptions made, documented and reasonable. | Proceed. Note assumptions and risks. |
| **Green** | 85-100% | Clear understanding. Ambiguities resolved with confidence. | Proceed. |

**Do not inflate confidence.** If you are between Yellow and Green, you are Yellow.

### Red confidence loop

If confidence is Red:

1. Present escalated ambiguities to the user in natural language with your assumptions and what is needed.
2. Wait for clarification.
3. Update `## Ambiguities` in state.
4. Re-resolve with user input.
5. Re-assess confidence.
6. Only proceed when confidence reaches Yellow or Green.

---

## Baseline handling

Baseline verifies the current app state. See [BASELINE-INTEGRATION.md](BASELINE-INTEGRATION.md) for the full workflow.

### Success

- Invoke the baseline skill workflow.
- Capture UI state and reproduce bugs if applicable.
- Record findings in state and debrief document.

### Failure

1. Stop. Do not proceed to document generation.
2. Explain what went wrong.
3. Present options:
   - **Retry** — try again after the user has fixed the environment.
   - **Fix config** — adjust the relevant configuration.
   - **Proceed without baseline** — continue debriefing, note baseline unavailable. Requires user approval.
   - **Abort** — stop the debrief and wait for direction.
4. Wait for user response. Do not choose an option yourself.
5. If user says proceed without:
   - Update state: `Baseline Status → Failed, User Override: Proceed without`.
   - Continue with debrief generation.
   - Note in document: *"Baseline unavailable — user opted to proceed without verification."*
6. If user guides you:
   - Attempt baseline again.
   - If success → proceed normally.
   - If still failing → return to step 2.

---

## Sparse ticket handling

If the ticket has minimal description:

1. Flag it immediately in chat.
2. Increase codebase exploration.
3. Check related tickets aggressively.
4. Lower confidence threshold — a sparse ticket with no code evidence is likely Yellow at best, possibly Red.
5. Do not invent requirements. If you cannot infer intent, escalate.

---

## Output template

Save to `.agents/context/debrief/{key}-{short-slug}.md`.

```markdown
---
skill: debrief
version: 3
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-06-26T08:42:00Z
updated_at: 2026-06-26T08:42:00Z
summary: "Auth guard race condition during token refresh."
status: In Progress
priority: High
debrief_status: complete
debrief_confidence: Green (90%)
baseline_status: complete
consumed_context:
  - .agents/context/baseline/OC-4644-SHB-362.md
artifacts_dir: OC-4644
---

# Debrief: OC-4644 — Auth guard race condition

<!-- STATUS: completed --> ## Overview
{1-2 paragraph synthesis}

<!-- STATUS: completed --> ## Metadata
| Field | Value |
|---|---|
| Assignee | {assignee} |
| Reporter | {reporter} |
| Created | {created} |
| Updated | {updated} |
| Labels | {labels} |
| Components | {components} |

<!-- STATUS: completed --> ## Problem Statement
{The bug or feature request in plain language}

<!-- STATUS: completed --> ## Acceptance Criteria / Desired Outcome
{Exact steps to reproduce, or "done" definition}

<!-- STATUS: completed --> ## Discussion Summary
{Key points from comments}

<!-- STATUS: completed --> ## Attachments Reviewed
| File | Summary |
|---|---|
| {filename} | {what it reveals} |

<!-- STATUS: completed --> ## Related Tickets
| Relation | Key | Summary |
|---|---|---|
| Parent | OC-4000 | Auth system improvements |

<!-- STATUS: completed --> ## Development Context
| PR / Branch / Commit | Summary |
|---|---|
| PR #123 | Initial auth refactor |

<!-- STATUS: completed --> ## Validity Assessment
{Is this still applicable? Blockers? Scope changes?}

<!-- STATUS: completed --> ## Codebase Evidence
| File | Relevance | What It Shows |
|------|-----------|---------------|
| `src/app/guards/auth.guard.ts` | High | Current role-based auth flow |

<!-- STATUS: completed --> ## Assumptions Resolved

### {what was unclear}
- **Assumption:** {what you believe}
- **Basis:** {ticket context + code evidence}
- **Confidence:** High (85%)
- **Alignment:** Fully aligned
- **What would disprove it:** {specific evidence}

<!-- STATUS: completed --> ## Assumptions Requiring Clarification
> Only include ambiguities with Low confidence or direct contradictions.

1. {ambiguity}
   - **Current best assumption:** {what you believe}
   - **Why it cannot be resolved:** {reason}
   - **What is needed:** {specific question}
   - **What would change my mind:** {specific evidence}

<!-- STATUS: completed --> ## Baseline Status
| Status | Notes |
|--------|-------|
| Complete | 3 screenshots captured, drag crash reproduced |

<!-- STATUS: completed --> ## Debrief Confidence
Green (90%) — root cause is clear, codebase evidence supports the assumption, baseline confirms reproduction.
```

---

## Versioning and migration

Debrief reports and state files follow the version in `SKILL.md`. See [VERSIONING.md](VERSIONING.md) for migration guidance.

- Current report frontmatter version: `3`.
- Current state frontmatter version: `3`.
- Older reports may be reused, but consumers should check freshness and version.

### Baseline report path

Baseline reports are read from:

```text
.agents/context/baseline/{scope}-{branch}.md
```

Not from the old `.agents/context/baseline/{key}/` directory.

---

## Presentation to user

Stream feedback during the process and summarize at the end.

### During process

> Researching `OC-1234`... found ticket, 12 comments, 3 attachments.
> Identified 3 ambiguities. Resolving 2 through codebase exploration...
> Resolved: "Which guard handles this?" → `auth.guard.ts`, High confidence (85%).
> Escalating 1 ambiguity: ticket contradicts itself on validation timing.

### After completion

1. **One-paragraph overview** — what the ticket is about and what needs to happen.
2. **Debrief confidence** — Green/Yellow/Red with %.
3. **Resolved ambiguities** — brief summary of what was unclear and how you resolved it.
4. **Escalated ambiguities** — numbered list with your assumptions and what is needed (only if any).
5. **Baseline status** — complete or unavailable with reason.
6. **Key evidence** — most important files or related tickets.

If confidence is Red, present escalated items and wait for user response before proceeding.
