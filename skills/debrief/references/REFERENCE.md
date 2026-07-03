# Debrief Reference

Research checklist, state management, context graph, ambiguity resolution, and output generation for `debrief` v4.0.

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
- [ ] **Non-English content** — preserve original text; translate only if a translation tool is configured.

---

## Delta mode / reuse existing debrief

Before starting full research, check for existing artifacts under the detected context directory.

1. **Check state file** — `{context_dir}/debrief/{key}/state.md`
   - If exists → read it. Resume from `## Phase Checklist` and `## Current Focus`.

2. **Check debrief document** — `{context_dir}/debrief/{key}-{slug}.md`
   - If exists and `generated_at` is recent (within `artifact_freshness_hours`) → read it as starting context.
   - Skip re-fetching ticket details unless the user asks for a refresh.
   - Skip re-scanning attachments unless something changed.
   - Re-resolve ambiguities with current codebase state.
   - Update the document in place rather than regenerating from scratch.

3. **Check freshness** — use `check-debrief-freshness.py` to compare branch, commit, and ticket `updated_at` against the report.

4. **If no existing debrief** → proceed with full research.

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

Path: `{context_dir}/debrief/{key}/state.md`

This is the investigator's working memory and the anchor for resuming after context compaction. Read it at the start of every iteration. Write to it before and after every subagent call.

```markdown
---
skill: debrief
version: 4.0
ticket: OC-4644
updated_at: 2026-07-03T08:42:00Z
---

# Debrief State: OC-4644

## Phase Checklist
- [x] Phase 0: Bootstrap
- [x] Phase 1: Gather evidence
- [x] Phase 2: Build context graph and identify ambiguities
- [ ] Phase 3: Resolve ambiguities
- [ ] Phase 4: Baseline
- [ ] Phase 5: Synthesize and validate
- [ ] Phase 6: Present

## Current Focus
Resolving ambiguities in ticket OC-4644.

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

## Visited Related Tickets
| Ticket | Depth | Visited At |
|---|---|---|
| OC-1234 | 1 | {iso} |
| OC-5678 | 2 | {iso} |

## Next Action
{what the next debrief iteration should do}
```

### Section rules

- **Phase Checklist:** Update after every subagent returns. This is the primary resume anchor.
- **Current Focus:** Update whenever the agent switches tasks. Be specific.
- **Last Completed Action:** Record what just finished and what it produced.
- **Session History:** Append only. Every iteration gets a row. Archive old rows when the table exceeds 20 rows.
- **Context Graph:** Add every source of evidence with relevance and contribution.
- **Ambiguities:** Update status on each iteration. Do not delete rows.
- **Codebase Explored:** Append only. Re-explore only if the ambiguity changed.
- **Baseline Status:** Update after each baseline attempt.
- **Ticket Context Cached:** Update when fresh tracker data is fetched.
- **Visited Related Tickets:** Maintain a visited set to prevent circular references.
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

Rate overall confidence in the entire debrief after ambiguity resolution and challenging. Use the v4 confidence calculation:

1. Start with the average confidence of all resolved assumptions.
2. Apply penalties:
   - `-10%` for each unresolved ambiguity that affects acceptance criteria.
   - `-5%` for each unresolved ambiguity that affects scope or interpretation.
   - `-15%` if the ticket contradicts related work or the codebase.
3. Floor at 0%, cap at 100%, round to the nearest 5%.

| Level | Range | Meaning | Action |
|-------|-------|---------|--------|
| **Red** | 0-59% | Too many unresolved ambiguities or contradictions. | Stop. Produce a blocker report. |
| **Yellow** | 60-84% | Some assumptions made, documented and reasonable. | Proceed. Note assumptions and risks. |
| **Green** | 85-100% | Clear understanding. Ambiguities resolved with confidence. | Proceed. |

**Do not inflate confidence.** If you are between Yellow and Green, you are Yellow.

### Confidence gap

When confidence is below 100%, document the gap in the frontmatter and in the report body:

```yaml
confidence_gap:
  - blocker: "Ticket does not specify expected behavior after refresh."
    why_it_blocks_full_confidence: "Could affect acceptance criteria."
    what_would_resolve_it: "PO confirmation or comment evidence."
    investigation_done: "Searched comments and related tickets; none found."
```

### Red confidence loop

If confidence is below `confidence_threshold` (default 85%):

1. Produce a blocker report at `{context_dir}/debrief/{key}-blockers.md`.
2. Present escalated ambiguities to the user in natural language with your assumptions and what is needed.
3. Wait for clarification.
4. Update `## Ambiguities` in state and the assumptions in the report.
5. Re-resolve with user input.
6. Re-assess confidence.
7. Only proceed when the user explicitly approves continuing despite low confidence or confidence reaches the threshold.

---

## Baseline handling

Baseline verifies current app state. It is a **soft default building block**: invoke it when the ticket involves verifiable state, but the user must approve proceeding without it. See [BASELINE-INTEGRATION.md](BASELINE-INTEGRATION.md).

### Success

- Delegate invocation to the `baseline-invoker` subagent.
- Capture UI state and reproduce bugs if applicable.
- Record findings in state and debrief document.

### Failure

1. Stop generating the debrief document until the user decides.
2. Explain what went wrong.
3. Present options:
   - **Retry** — try again after the user has fixed the environment.
   - **Fix config** — adjust the relevant configuration.
   - **Proceed without baseline** — continue the debrief, note baseline unavailable. Requires explicit user approval.
   - **Abort** — stop the debrief and wait for direction.
4. Wait for user response. Do not choose an option yourself.
5. If user says proceed without:
   - Update state: `Baseline Status → Failed, User Override: Proceed without`.
   - Continue with debrief generation.
   - Note in document: *"Baseline unavailable — user opted to proceed without verification."*

---

## Sparse ticket handling

If the ticket has minimal description:

1. Flag it immediately in chat.
2. Increase codebase exploration.
3. Check related tickets aggressively.
4. Lower confidence threshold — a sparse ticket with no code evidence is likely Yellow at best, possibly Red.
5. Do not invent requirements. If you cannot infer intent, escalate.
6. Produce a blocker report if confidence remains Red.

---

## Generic artifact discovery

Discover related reports by schema and relationship, not by skill name.

1. Run `related-context-scanner` to scan `{context_dir}/` for `.md` files matching the ticket or branch.
2. Rank matches by: exact match, skill relevance, recency, user priority.
3. Process the top 10 by default. If more are needed, continue down the ranked list or ask the user.
4. Flag stale artifacts (older than `artifact_freshness_hours`) but still consume them with caveats.

---

## Duplicate and already-implemented detection

Before deep investigation, check whether the ticket is already done or duplicated.

1. Run `duplicate-detector` to search the tracker and git state.
2. Possible statuses: `none`, `duplicate`, `already_implemented`, `partially_implemented`.
3. Surface the result to the user and ask whether to continue, pivot, or stop.

---

## Task type classification

Classify the ticket early to decide which phases apply.

| Type | Enables |
|---|---|
| `code` | `code-explorer`; baseline may be relevant. |
| `ui` | `code-explorer`; baseline is usually relevant. |
| `docs` | Skip `code-explorer` unless user overrides; baseline rarely relevant. |
| `process` | Skip `code-explorer` unless user overrides; baseline rarely relevant. |
| `unknown` | Ask user or proceed with all phases cautiously. |

Use `infer-ticket-type.py` and `detect-verifiable-state.py` to inform the decision.

---

## Output template

Save to `{context_dir}/debrief/{key}-{short-slug}.md`.

```markdown
---
skill: debrief
version: 4.0
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-07-03T08:42:00Z
updated_at: 2026-07-03T08:42:00Z
summary: "Auth guard race condition during token refresh."
task_type: code
status: In Progress
priority: High
debrief_status: complete
debrief_confidence: Green (90%)
confidence_gap: []
baseline_status: complete
consumed_context:
  - {context_dir}/baseline/OC-4644-SHB-362.md
artifacts_dir: OC-4644
assumptions:
  - assumption: "Token refresh happens in auth.guard.ts."
    basis: "Code in auth.guard.ts contains refresh logic; no interceptor found."
    confidence: 85
    alignment: Reasonable inference
    disproof_signals: "ADR mentioning interceptor, code in interceptor, tests referencing refresh.interceptor."
    impact_if_wrong: "Fix would move to interceptor."
    status: resolved
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
- **Confidence:** 85
- **Alignment:** Reasonable inference
- **Disproof signals:** {specific evidence}
- **Impact if wrong:** {how implementation would change}
- **Status:** resolved

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

<!-- STATUS: completed --> ## Confidence Gap
> Only include when confidence is below 100%.

- **Blocker:** {what is missing}
- **Why it blocks full confidence:** {impact}
- **What would resolve it:** {specific evidence or clarification}
- **Investigation done:** {what was searched}

<!-- STATUS: completed --> ## Debrief Confidence
Green (90%) — root cause is clear, codebase evidence supports the assumption, baseline confirms reproduction.
```

---

## Blocker report template

Save to `{context_dir}/debrief/{key}-blockers.md` when confidence is below `confidence_threshold`.

```markdown
---
skill: debrief
type: blocker-report
version: 4.0
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-07-03T08:42:00Z
updated_at: 2026-07-03T08:42:00Z
summary: "Ticket is too vague to proceed with confidence."
---

## What is known
- ...

## What was investigated
- ...

## What is missing
- ...

## Why the risk is too high
- ...

## What the user needs to clarify
1. ...
```

---

## Versioning and migration

Debrief reports and state files follow the version in `SKILL.md`. See [VERSIONING.md](VERSIONING.md) for migration guidance.

- Current report frontmatter version: `4.0`.
- Current state frontmatter version: `4.0`.
- Older reports may be reused, but consumers should check freshness and version.

### Baseline report path

Baseline reports are read from:

```text
{context_dir}/baseline/{scope}-{branch}.md
```

Not from the old `{context_dir}/baseline/{key}/` directory.

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
7. **Suggested tools** — if a helpful tool exists but is not configured (generic categories only).

If confidence is Red, present the blocker report and wait for user response before proceeding.
