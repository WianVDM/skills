# Detailed Reference

State file specification, conductor loop, and artifact formats for `orchestrate`.

## State file specification

Path: `.agents/context/orchestrate/{key}/state.md`

```markdown
# Orchestrate State: {key}

## Understanding
{2-5 paragraphs synthesizing what is known. Update each loop. Be specific.}

## Confidence
{Red | Yellow | Green} ({0-100}%) — {one sentence explaining why}

## Open Questions
- [ ] {question} (blocking: yes/no)
- [x] {resolved question} → {how it was resolved}

## Skill Log
| # | Skill | Why It Was Run | Key Finding | Confidence After |
|---|-------|----------------|-------------|------------------|
| 1 | plan-next | initial evaluation | recommended diagnose + grill-with-docs | Yellow |

## References
- `src/app/guards/auth.guard.ts` — race condition location
- `docs/adr/0003-auth-flow.md` — relevant architectural decision

## Decisions
| Decision | Reasoning | Mode |
|----------|-----------|------|
| Run diagnose before grill-with-docs | plan-next ranked it essential; baseline confirms bug is reproducible | interactive/auto |

## Next Action
{exactly what orchestrate will do next, and why}
```

### Section rules

- **Understanding:** Replace the entire section on each update. Do not append.
- **Confidence:** Be honest. Yellow means *"I could plan but I'd be guessing on edge cases."* Green means *"I can explain this to a colleague and they'd agree."*
- **Open Questions:** Add new ones as they appear. Check off resolved ones with a brief note.
- **Skill Log:** Append only. This is the audit trail.
- **References:** Add file paths, ADRs, docs, or code snippets that matter.
- **Decisions:** Log every choice about which skill to run next, whether to loop, or whether to present the plan.
- **Next Action:** Update this before doing anything.

## The conductor loop

### Entry points

**Fresh start:** No state.md exists.
- Create state.md with empty sections.
- Read debrief + baseline.
- Write initial understanding and confidence (likely Yellow or Red).
- Set next action: `Run plan-next to evaluate skills.`

**Resume:** State.md exists.
- Read it in full.
- Read the latest checkpoint if present.
- Read decisions, assumptions, and the current phase contract if execution is in progress.
- Resume from `## Next Action`.

### Loop steps

1. Read state.md.
2. Check exit condition:
   - Confidence is Green (≥85%)?
   - No blocking open questions?
   - Challenge gate passed?
   - Understanding is specific enough to explain implementation to a colleague?
   - If yes → draft plan.
3. Decide next skill. See [Skill routing](#skill-routing).
4. Run the skill through the skill-executor.
5. Absorb findings.
6. Ask the confidence-assessor to update confidence.
7. Write state.md.
8. Loop.

### Challenge gate (mandatory before exiting loop)

Before exiting the loop and drafting a plan, actively challenge understanding.

**When:** Every time confidence reaches Green (≥75%).

**How:**
1. State current understanding and confidence in `## Decisions`.
2. Run one challenge skill from the configured `preferred_challenge_skills`.
3. Absorb findings into state.md.
4. If the challenge reveals any new gap, contradiction, or overlooked edge case:
   - Lower confidence.
   - Add to `## Open Questions`.
   - Continue looping.
5. Only if the challenge confirms understanding with no new gaps may the gate be marked passed.

**Rules:**
- Must run even for small tickets.
- Must be different from the last skill run.
- Still required in auto mode.

## Skill routing

### When to run plan-next
- First iteration.
- After a major finding changes the landscape.
- When no clear skill would help most.
- After resolving a blocking question and needing to re-evaluate.

### When to run a skill directly
- State clearly indicates the next gap.
- Plan-next previously recommended a sequence and you are working through it.
- Baseline shows a reproducible bug.
- Requirements are ambiguous.

### Routing rules
- Prefer depth over breadth.
- If plan-next recommends many skills, pick the top 1-2 that address the biggest gap.
- Re-run plan-next after any skill that significantly changes understanding.

## Plan format

Path: `.agents/context/orchestrate/{key}/plan.md`

```markdown
# Plan: {key} — {brief title}

## Understanding
{2-3 sentence summary}

## Phases

### Phase 1: {Name}
- **Skills:** {skill list}
- **Work:** {what will be done}
- **Checklist:**
  - [ ] {concrete, verifiable task}
  - [ ] {concrete, verifiable task}
- **Why:** {rationale}
- **Validation:** {how we will know it worked}
- **Out of bounds:** {what this phase must not touch}

## Risks
- {risk} → {mitigation}

## Out of Scope
- {what is explicitly not included}
```

## Phase contract format

Path: `.agents/context/orchestrate/{key}/phase-{N}.md`

```markdown
# Phase {N}: {title}

## Goal
{one sentence describing the outcome}

## In-scope files
- `{file path}` — {what change it will receive}

## Out-of-scope files
- `{file path}` — {explicitly what this phase will not touch}

## Expected behavioral change
{what behavior will change after this phase}

## Checklist
- [ ] {concrete task}
- [ ] {concrete task}

## Dependencies on previous phases
- {phase M must be complete because ...}

## Risks and verification
- {risk} → {how to verify it did not materialize}
```

## Decision log format

Path: `.agents/context/orchestrate/{key}/decisions.md`

```markdown
# Decisions: {key}

## DEC-001 — {short title}
- **Date:** {iso-date}
- **Context:** {what was known}
- **Decision:** {what was decided}
- **Rationale:** {why}
- **Rejected alternatives:** {what was considered and rejected}
- **Consequences:** {what this forces or enables}
- **Linked checkpoint:** `.agents/context/handoff/{key}-checkpoint.md` at {iso-date}
```

Rules:
- Decision IDs are sequential.
- Never edit past decisions; append a new entry that supersedes if reversed.

## Assumption log format

Path: `.agents/context/orchestrate/{key}/assumptions.md`

```markdown
# Assumptions: {key}

## ASS-001 — {short description}
- **Date:** {iso-date}
- **Assumption:** {the thing taken as true}
- **Affects:** {phases or decisions}
- **Validation status:** {unvalidated | validated | invalidated}
- **Validation method:** {how it will be or was checked}
- **Impact if false:** {what happens if the assumption is wrong}
```

## Final summary format

Path: `.agents/context/orchestrate/{key}/runbook.md`

```markdown
### Execution Summary
- **Ticket:** {key}
- **Mode:** {interactive | auto}
- **Skills invoked:** {ordered list}
- **Conductor loops:** {count}
- **Auto-decisions:** {list}
- **Code files modified:** {list}
- **UI tests performed:** {count}
- **Branch verification:** {pass/warn/fail}
```
