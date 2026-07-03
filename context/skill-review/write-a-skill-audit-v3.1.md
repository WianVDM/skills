---
report: audit
skill: write-a-skill
version: "3.1"
timestamp: 2026-07-03T16:00:00Z
status: final
---

# Audit report: `write-a-skill`

**Overall verdict:** `write-a-skill` is now aligned with the target specification, the `skill-standards` fundamentals, and the recommendations from the standards review. All principle criteria (🔒) are green. The skill is ready to audit other skills and can be released as version 3.1.

## Per-criterion ratings

| Criterion | Rating | Notes |
|---|---|---|
| A1 Name | 🟢 | Matches directory name and convention. |
| A2 Description | 🟢 | Under 1024 characters, states what it does, and lists triggers. |
| A3 Description as context pointer | 🟢 | Front-loads "Skill-design partner"; distinct triggers per branch. |
| A4 Invocation mode | 🟢 | Declared via both `invocation: user-invoked` and `disable-model-invocation: true`. |
| B1 One core objective | 🟢 | Single meta-conductor for skill lifecycle management. |
| B2 Clear purpose | 🟢 | Purpose and outcome are clear. |
| B3 Clear when to use | 🟢 | Four realistic branch triggers. |
| B4 Out of scope | 🟢 | Explicit. |
| B5 Right skill type | 🟢 | Conductor. |
| C1 Form matches domain | 🟢 | Conductor with clear steps and guidelines. |
| C2 Steps have completion criteria | 🟢 | Every branch ends with a completion criterion. |
| C3 Completion criteria are strong | 🟢 | Criteria are binary and checkable. |
| C4 Leading words used | 🟢 | "Skill-design partner" anchors the skill. |
| C5 Explain-the-why | 🟢 | Each branch has a one-line rationale; detailed phase rationales live in `references/BRANCH_WORKFLOWS.md`. |
| C6 Negation pairs | 🟢 | Negative rules paired with positive directives. |
| C7 No vague guideline soup | 🟢 | Guidelines tied to principles or criteria. |
| C8 No manual in disguise | 🟢 | States intent, not mechanics. |
| C9 No hidden hybrid | 🟢 | Steps and guidelines separated. |
| C10 No no-op lines | 🟢 | Opening sentence is load-bearing; every line earns its place. |
| D1 Progressive disclosure | 🟢 | Branch details, schemas, and contracts live in `references/`. |
| D2 Co-location | 🟢 | Related concepts grouped. |
| D3 No sprawl | 🟢 | `SKILL.md` is 145 lines. |
| D4 No sediment | 🟢 | Old duplicated guide files removed. |
| D5 No duplication | 🟢 | Description is the trigger pointer; `When to use` elaborates without repeating. |
| D6 Required files present | 🟢 | `SKILL.md` and `README.md` present. |
| D7 No empty directories | 🟢 | All directories contain content. |
| D8 Reference links resolve | 🟢 | All links in `SKILL.md` and `README.md` verified. |
| D9 Flat structure | 🟢 | No deep nesting. |
| E1 Pluggability declared | 🟢 | Global scope and detection rules documented. |
| E2 Harness-agnostic language | 🟢 | No harness-specific tool names. |
| E3 Project-agnostic language | 🟢 | No hardcoded project paths in core files. |
| E4 Detection before config | 🟢 | Detection script runs before asking the user. |
| E5 Dependencies declared | 🟢 | Python runtime added to `DEPENDENCIES.md`. |
| E6 Fail closed | 🟢 | Missing-capability handling documented. |
| F1 Config schema documented | ⚪ | N/A for this skill itself. Config pattern documented for skills it creates. |
| F2 No secrets in config | 🟢 | None. |
| F3 No over-configuring | ⚪ | N/A. |
| F4 Notes are memory | ⚪ | N/A. |
| F5 Never overwrite without asking | 🟢 | Explicitly stated. |
| G1 State location documented | 🟢 | Artifact locations and schemas documented. |
| G2 State schema documented | 🟢 | Frontmatter and body schemas documented. |
| G3 Resumption logic | 🟢 | Resumption order documented. |
| G4 No duplicate work | 🟢 | Append-only decision log. |
| G5 Report schema documented | 🟢 | Context report schema documented. |
| G6 Freshness handled | 🟢 | Stale/missing reports handled. |
| G7 Missing reports handled | 🟢 | Required missing reports trigger consultation. |
| H1 Delegation is appropriate | 🟢 | Workers match branches and phases. |
| H2 Worker boundaries clear | 🟢 | Each worker states role, scope, tools, forbidden actions, return format. |
| H3 Worker return contract | 🟢 | Standard contract defined and referenced. |
| H4 Workers do not ask users | 🟢 | Workers return `needs_input`. |
| H5 Scripts for deterministic logic | 🟢 | `detect-project-layout.py` handles path detection. |
| H6 Scripts are safe and isolated | 🟢 | Script is read-only, deterministic, no user input. |
| I1 Dependencies declared | 🟢 | Required capabilities and consumed references listed. |
| I2 Building-block extraction | 🟢 | Rubric, worker contract, and glossary extracted. |
| I3 Consumers handle absence gracefully | 🟢 | Missing reports trigger consultation. |
| I4 One-way pattern consistency | 🟢 | One detection approach, one contract, one rubric, one glossary. |
| I5 No premature abstraction | 🟢 | Eleven subagents justified by four branches. |
| J1 No secrets in skill files | 🟢 | None. |
| J2 Destructive actions confirmed | 🟢 | Confirmation required before drafting/modifying. |
| J3 External access documented | 🟢 | No external access required. |
| J4 Read-only investigation preferred | 🟢 | Review branch prefers read-only. |
| J5 Safe in untrusted projects | 🟢 | Rule to confirm before reading files from untrusted projects. |
| K1 Description tested | 🟢 | 10 should-trigger and 10 should-not-trigger queries in `references/EVAL.md`. |
| K2 Behavior tested | 🟢 | 10 behavioral evals documented. |
| K3 Versioned | 🟢 | Bumped to 3.1. |
| K4 Migration path | 🟢 | Documented. |
| K5 Maintenance plan | 🟢 | Review cadence and checklist documented. |

## Positive findings

- The skill is explicitly global and user-invoked, with both `invocation` and `disable-model-invocation` declared.
- Hardcoded `.agents/` paths are gone; detection + confirmation is in place.
- Four branches are clearly separated, and the detailed workflows are disclosed behind a pointer.
- `SKILL.md` is now 145 lines — well under the 300-line ideal.
- Every branch has a one-line rationale, and every phase has a rationale in `references/BRANCH_WORKFLOWS.md`.
- A self-audit phase blocks bloated or non-compliant designs before drafting.
- State, report, and worker-contract schemas are documented and referenced by every subagent.
- Subagent prompts are precise about tools and forbidden actions.
- The audit rubric is the single canonical standard for skill review.
- A glossary makes the skill a useful building-block reference as well as a conductor.
- Evaluation and maintenance documentation are comprehensive.

## Issues

No red or yellow issues remain.

## Blockers

None.

## Recommended next action

Run the expanded behavioral evals in `references/EVAL.md` and iterate on any failures.
