# Reference

Detailed guidance for `plan-next`: context ingestion, readiness audit, skill evaluation, plan construction, and finalization.

---

## 1. Ingest context

Three input modes:

1. **Document path** — read the file.
2. **Freeform text** — treat the quoted text as context.
3. **Session context** — summarize the current conversation and check for existing reports in `.agents/context/`.

Also check for existing reports from other skills:

| Source | Location | Use |
|--------|----------|-----|
| Debrief | `.agents/context/debrief/{key}-report.md` | Ticket understanding, scope, assumptions |
| PR report | `.agents/context/pr-report/{key}-report.md` | PR feedback, open issues, CI status |
| Baseline | `.agents/context/baseline/{key}-report.md` | UI evidence, reproduction results |
| Diagnose | `.agents/context/diagnose/{key}-report.md` | Root-cause analysis |

Note the freshness of each report. If a report is older than the latest relevant event, flag it as stale.

Always produce a 2-3 sentence context summary before proceeding.

---

## 2. Readiness check

Audit whether the context is sufficient to act on.

### Common gap indicators

- Unresolved blocker comments, especially from hybrid or human reviewers.
- Behavioral changes mentioned but not explained.
- Inconsistencies between request and implementation.
- Missing error handling, edge cases, or test coverage.
- Tentative language: "should", "consider", "might", "risk", "break".
- Changes touching state management, domain logic, or cross-component flows.
- UI changes without visual verification.
- Multiple reviewer concerns that seem related but are not obviously connected.
- Unknown unknowns — things the agent might be wrong about but has not checked.

### Readiness levels

| Level | Meaning |
|-------|---------|
| **Green** | Trivial, single-file, no ambiguity, no blockers. |
| **Yellow** | Some complexity or open questions. |
| **Red** | Blockers, behavioral changes, or architectural concerns. |

Bias: if readiness is Yellow or Red, boost deep-dive skills toward Essential unless clearly irrelevant.

---

## 3. Discover and profile skills

### Discovery

Find all skill directories under configured `skill_search_paths`. Read each `SKILL.md` frontmatter:

- `name`
- `description`
- `license`
- `metadata`

Build a catalog with name, description, triggers, and declared skill type if present.

### Profiling

For each skill, build a capability profile. On first encounter, read:

- `SKILL.md` — intent, when to use, core workflow, out-of-scope
- `references/CAPABILITIES.md` — what it detects/consumes
- `references/CONTEXT_REPORTS.md` — what it produces
- `references/CHECKPOINTING.md` — how heavy/long it is
- `references/VALIDATION.md` — when it is considered complete

On subsequent encounters, use a curated subset to refresh without re-reading everything. Re-read the full references periodically (e.g., after a skill changes or when the evaluator is uncertain).

The profile should capture:

- **Triggers** — when the skill activates.
- **Inputs** — what context it consumes.
- **Outputs** — what reports or artifacts it produces.
- **Cost** — light / medium / heavy.
- **Depth** — surface / diagnostic / domain-alignment.
- **Verification value** — does it confirm correctness?
- **Typical position** — understand / implement / verify.

---

## 4. Evaluate all skills

Produce a complete evaluation for every discovered skill.

| Skill | Verdict | Direct | Risk | Depth | Verify | Cost | Reasoning |
|-------|---------|--------|------|-------|--------|------|-----------|

**Verdicts:** Essential / Recommended / Optional / Not applicable.

**Scoring dimensions (1-5 or yes/no):**

- **Direct** — addresses a visible gap.
- **Risk** — prevents wrong assumptions or missed edge cases.
- **Depth** — moves to root cause or domain alignment.
- **Verify** — confirms correctness.
- **Cost** — lighter is better for trivial issues.

**Reasoning rules:**

- Be specific. Tie the skill to exact findings in the context.
- If Not applicable, explain what context would make it applicable.
- If Optional, explain the trade-off.
- If Essential or Recommended, cite the exact gap or need.
- Do not omit any skill.

**Deep-dive bias:**

- If readiness is Yellow or Red, `diagnose`, `grill-with-docs`, and similar deep-dive skills should be strongly considered even if direct relevance seems low.
- Surface-level issues often have deeper roots. The skill evaluator must value risk reduction and depth.

---

## 5. Propose phased plan

Group Essential and Recommended skills into 2–4 phases.

### Default phase templates

#### PR review context

- Phase 1: Understand — `diagnose` or `grill-with-docs` if root cause or domain alignment is unclear.
- Phase 2: Implement — direct work.
- Phase 3: Verify — `verify-branch`, `baseline` if UI changed.

#### Bug report context

- Phase 1: Diagnose — root-cause analysis.
- Phase 2: Fix — direct work.
- Phase 3: Verify — `verify-branch`, `baseline` if relevant.

#### Feature request context

- Phase 1: Plan — `debrief`, `grill-with-docs`, `to-prd` for domain alignment and specification.
- Phase 2: Prototype — `prototype` if the design is uncertain.
- Phase 3: Implement — direct work.
- Phase 4: Verify — `verify-branch`, `baseline`.

These are examples, not hard rules. Map actual discovered skills to the roles dynamically.

### Phase structure

Each phase must include:

- **Name** — e.g., "Understand", "Diagnose", "Implement", "Verify".
- **Skills** — specific skill names to invoke.
- **Why** — why these skills fit this phase.
- **Expected output** — artifact or state to produce.
- **Dependencies** — previous phases or artifacts required.
- **Checkpoint** — whether a pause or handoff is recommended before the next phase.

### Dependency notation

```markdown
### Phase 2: Implement
- **Skills:** ...
- **Depends on:** Phase 1 (root cause confirmed)
- **Expected output:** Code changes + tests
- **Checkpoint:** `/handoff {key}` recommended if implementation spans multiple sessions
```

---

## 6. Present and confirm

Output to the user in this order:

1. **Context summary** — 2-3 sentences.
2. **Readiness level** — Green/Yellow/Red with rationale.
3. **Full skill evaluation matrix** — complete table from section 4.
4. **Proposed phased plan** — phases with skills, why, expected output, dependencies, checkpoints.
5. **Confirmation prompt** — ask the user:

   > Does this plan look right? I can:
   > - **Make it more detailed** — break phases into granular steps with specific files/actions
   > - **Use more specific skills** — narrow recommendations to exact skill invocations with arguments
   > - **Be more flexible** — add contingency branches, optional phases, or alternative approaches
   > - **Adjust phases** — reorder, merge, split, or add/remove phases based on your input
   > - **Proceed as-is** — finalize and save the plan

Do not save the finalized plan yet. Wait for explicit confirmation.

---

## 7. Iterate and show revision diffs

If the user asks for changes:

- Apply the changes to the draft plan.
- Show a concise diff: what was added, removed, or reordered.
- Re-present the full skill evaluation matrix + updated plan.
- Ask for confirmation again.

Auto-save the draft after every change.

### Diff format

```markdown
### Changes from revision 1
- Added `grill-with-docs` to Phase 1 (domain alignment concern).
- Split Phase 2 into two phases: backend changes and frontend changes.
- Removed `prototype` (user confirmed design is clear).
```

---

## 8. Finalize

When the user confirms:

1. Copy `.agents/context/plan-next/{key}-plan-draft.md` to `.agents/context/plan-next/{key}-plan.md`.
2. Update state: `status: finalized`, `finalized_at: {iso}`.
3. Log the final decision in `.agents/context/plan-next/{key}-decisions.md`.
4. Present post-plan guidance.

---

## 9. Plan template

```markdown
---
skill: plan-next
version: 1.0.0
key: OC-1234
status: finalized
updated_at: 2026-06-26T08:00:00Z
---

# Plan: {brief title}

## Context Summary
{2-3 sentences}

## Readiness
{Green | Yellow | Red} — {brief rationale}

## Phase 1: {Name}
- **Skills:** {skill list}
- **Why:** {rationale}
- **Expected output:** {artifact or state}
- **Depends on:** {none | previous phase / artifact}
- **Checkpoint:** {handoff recommended?}

## Phase 2: {Name}
...

## Action Items
1. {immediate next step}
2. ...

## Notes
- {risks, dependencies, out-of-scope items, alternatives}
```

---

## 10. Post-plan guidance

After finalization:

- Surface the file path.
- List the top 3 immediate action items.
- Recommend the first skill to run.
- Mention handoff checkpoints between heavy phases if applicable.
