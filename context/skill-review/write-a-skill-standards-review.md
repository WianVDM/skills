---
report: standards-review
skill: write-a-skill
version: "3.1"
timestamp: 2026-07-03T14:00:00Z
status: final
reviewers: internal
standards: skill-standards package (G:/My Drive/.agents/docs/skill-standards)
inspiration: mattpocock/skills/skills/productivity/writing-great-skills
---

# Standards review: `write-a-skill` (post-refactor)

**Overall verdict:** The refactored skill is a strong, well-aligned conductor. It now meets the project target spec and the `skill-standards` fundamentals. No red findings. A handful of yellow items and two or three small improvements inspired by Matt Pocock's `writing-great-skills` would make it even tighter.

## Methodology

Reviewed against:

1. The project target spec (`context/skill-design/write-a-skill-target-spec.md`).
2. The `skill-standards` package in `G:/My Drive/.agents/docs/skill-standards`.
3. Matt Pocock's `writing-great-skills` (`SKILL.md` and `GLOSSARY.md`).

The rubric used is the skill's own `references/AUDIT_RUBRIC.md`.

## Ratings

| Criterion | Rating | Notes |
|---|---|---|
| A1 Name | 🟢 | Matches directory and convention. |
| A2 Description | 🟢 | Under 1024 chars, states what it does and lists triggers. |
| A3 Description as context pointer | 🟢 | Front-loads "Skill-design partner"; distinct branches. |
| A4 Invocation mode | 🟡 | Declared `invocation: user-invoked`, but the standard field used by Matt Pocock and many harnesses is `disable-model-invocation: true`. Add it to be unambiguous. |
| B1 One core objective | 🟢 | Single meta-conductor for skill lifecycle. |
| B2 Clear purpose | 🟢 | Purpose and outcome are explicit. |
| B3 Clear when to use | 🟢 | Four realistic branch triggers. |
| B4 Out of scope | 🟢 | Explicit. |
| B5 Right skill type | 🟢 | Conductor. |
| C1 Form matches domain | 🟢 | Conductor with steps + guidelines. |
| C2 Steps have completion criteria | 🟢 | Every phase ends on a checkable condition. |
| C3 Completion criteria are strong | 🟢 | Mostly checkable and exhaustive. |
| C4 Leading words used | 🟢 | "Skill-design partner" anchors invocation. |
| C5 Explain-the-why | 🟡 | User-interaction rules explain reasoning; individual workflow phases lack one-line rationales. |
| C6 Negation pairs | 🟢 | Prohibitions are paired with positive directives. |
| C7 No vague guideline soup | 🟢 | Guidelines tied to principles or criteria. |
| C8 No manual in disguise | 🟢 | Intent-level, not mechanics. |
| C9 No hidden hybrid | 🟢 | Steps and guidelines separated. |
| C10 No no-op lines | 🟡 | Opening sentence "A conductor skill that helps..." largely restates the description. |
| D1 Progressive disclosure | 🟢 | Schemas, contracts, and detailed checklists live in `references/`. |
| D2 Co-location | 🟢 | Related concepts are grouped. |
| D3 No sprawl | 🟡 | `SKILL.md` is ~240 lines because it hosts all four branch workflows. Consider moving per-branch detail to a disclosed reference. |
| D4 No sediment | 🟢 | Old duplicated guide files were removed. |
| D5 No duplication | 🟡 | The description's four triggers are repeated almost verbatim in `When to use`. Minor duplication. |
| D6 Required files present | 🟢 | `SKILL.md` and `README.md` present. |
| D7 No empty directories | 🟢 | All directories contain content. |
| D8 Reference links resolve | 🟢 | All `SKILL.md` and `README.md` links verified. |
| D9 Flat structure | 🟢 | No deep nesting. |
| E1 Pluggability declared | 🟢 | Global scope and detection rules documented. |
| E2 Harness-agnostic language | 🟢 | No harness-specific tool names. |
| E3 Project-agnostic language | 🟢 | No hardcoded project paths in core files. |
| E4 Detection before config | 🟢 | Detection script runs before asking. |
| E5 Dependencies declared | 🟡 | Detection script requires Python, which is not explicitly listed in `DEPENDENCIES.md`. |
| E6 Fail closed | 🟢 | Missing-capability handling is documented. |
| F1 Config schema documented | ⚪ | N/A for this skill itself. Config pattern is documented for skills it creates. |
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
| I2 Building-block extraction | 🟢 | Rubric and worker contract extracted. |
| I3 Consumers handle absence gracefully | 🟢 | Missing reports trigger consultation. |
| I4 One-way pattern consistency | 🟢 | One detection approach, one contract, one rubric. |
| I5 No premature abstraction | 🟢 | Eleven subagents are justified by four branches. |
| J1 No secrets in skill files | 🟢 | None. |
| J2 Destructive actions confirmed | 🟢 | Confirmation required before drafting/modifying. |
| J3 External access documented | 🟢 | No external access required. |
| J4 Read-only investigation preferred | 🟢 | Review branch prefers read-only. |
| J5 Safe in untrusted projects | 🟢 | Added a rule to confirm before reading files from untrusted projects. |
| K1 Description tested | 🟡 | Only four trigger evals; the standards package recommends 10 should-trigger + 10 should-not-trigger for model-invoked skills. Even for a user-invoked skill, expanding the eval set strengthens confidence. |
| K2 Behavior tested | 🟢 | Behavioral evals documented. |
| K3 Versioned | 🟢 | Bumped to 3.1. |
| K4 Migration path | 🟢 | Documented. |
| K5 Maintenance plan | 🟢 | Review cadence and checklist documented. |

## Positive findings

- The skill is explicitly framed as a global, user-invoked conductor.
- Hardcoded paths are gone; detection + confirmation is in place.
- Four branches are clearly separated with distinct workflows and completion criteria.
- A self-audit phase and anti-over-complication checks are now part of the design workflow.
- State, report, and worker-contract schemas are documented and referenced by every subagent.
- Subagent prompts are precise about tools and forbidden actions.
- The audit rubric is now the single canonical standard for skill review.
- Security and untrusted-project handling are addressed.

## Issues and recommendations

### 1. Add `disable-model-invocation: true` to the frontmatter (A4)

**Observation:** The skill declares `invocation: user-invoked`, but the convention used by Matt Pocock's `writing-great-skills` and many harnesses is `disable-model-invocation: true`. Without that field, a harness that does not understand the custom `invocation` field may still load the description into the model's context.

**Recommendation:** Add `disable-model-invocation: true` to `SKILL.md` frontmatter. Keep `invocation: user-invoked` if the project target spec requires it, or move it to `metadata:` as a custom project field.

```yaml
---
name: write-a-skill
description: Skill-design partner. Use when creating a new skill, reviewing a skill, upgrading a skill, or deciding whether a problem deserves a skill.
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "3.1"
  scope: global
invocation: user-invoked
disable-model-invocation: true
---
```

### 2. Remove or sharpen the opening no-op sentence (C10)

**Observation:** The first body sentence reads: *"A conductor skill that helps design, draft, review, and upgrade agent skills according to the `skill-standards` fundamentals."* It largely restates the description.

**Recommendation:** Replace it with a load-bearing sentence that explains the user-facing contract:

> "Use this skill as a design partner that will not draft files until the design and a self-audit pass the fundamentals."

### 3. Add one-line rationales to each workflow phase (C5)

**Observation:** The phases say *what* to do but not *why* the phase reduces risk.

**Recommendation:** Append a brief rationale to each phase, e.g.:

> **Why this phase exists:** Clarifying intent first prevents designing a skill for the wrong problem.

This can be done inline without adding much length.

### 4. Push per-branch workflow detail into a disclosed reference (D3)

**Observation:** `SKILL.md` is ~240 lines because it contains the full step sequences for New, Quick, Review, and Upgrade.

**Recommendation:** Create `references/BRANCH_WORKFLOWS.md` containing the detailed workflows. In `SKILL.md`, keep only:

- A one-line summary of each branch.
- Its completion criterion.
- A pointer to `references/BRANCH_WORKFLOWS.md` for the full phase list.

This would bring `SKILL.md` closer to the 300-line ideal and improve progressive disclosure.

### 5. Reduce description / `When to use` duplication (D5)

**Observation:** The description lists four triggers; the `When to use` section repeats them with slightly different wording.

**Recommendation:** Make the description the pure trigger pointer and the body section the expansion. For example:

```yaml
description: Skill-design partner. Use when creating, reviewing, upgrading, or deciding whether a problem deserves a skill.
```

Then the body section can elaborate on each branch.

### 6. Declare Python as a required capability (E5)

**Observation:** `scripts/detect-project-layout.py` requires a Python interpreter, but `references/DEPENDENCIES.md` does not list it.

**Recommendation:** Add to `DEPENDENCIES.md`:

> - **Python 3.x** — required to run `scripts/detect-project-layout.py`.

### 7. Expand the trigger eval set (K1)

**Observation:** `references/EVAL.md` contains one trigger eval per branch (four total). The `skill-standards` package recommends 10 should-trigger and 10 should-not-trigger queries for model-invoked skills.

**Recommendation:** Even though `write-a-skill` is user-invoked, expand the eval set to include near-miss cases such as:

- "I want to change the prompt for my agent" — should not trigger a new skill.
- "Can you write a Python script that checks my PRs?" — should trigger the alternatives branch.
- "Review this skill file" — should trigger Review.
- "Make this skill work in any project" — should trigger Upgrade.

A set of 10 should-trigger and 10 should-not-trigger queries would make the description more defensible and help catch future drift.

## Cross-inspiration from Matt Pocock's `writing-great-skills`

Matt's skill treats a skill as a **determinism device** whose root virtue is **predictability**. The refactored `write-a-skill` already acts on that virtue (completion criteria, self-audit, no hidden assumptions). Two ideas from Matt are worth borrowing:

1. **A skill glossary.** Matt's `GLOSSARY.md` defines every bold term. `write-a-skill` could add a `references/GLOSSARY.md` defining terms such as `leading word`, `completion criterion`, `branch`, `context pointer`, `legwork`, `premature completion`, `sediment`, `sprawl`, and `no-op`. This would turn the skill into a building-block reference as well as a conductor.
2. **Even more aggressive disclosure.** Matt's skill keeps `SKILL.md` very short because almost everything is reference. `write-a-skill` is a conductor, so it needs steps, but the detailed branch workflows can still be disclosed behind a pointer.

## Blockers

None.

## Recommended next actions

1. Add `disable-model-invocation: true` to `SKILL.md` frontmatter.
2. Sharpen the opening sentence and add one-line rationales to phases.
3. Move detailed branch workflows to `references/BRANCH_WORKFLOWS.md`.
4. Tighten the description and reduce duplication with `When to use`.
5. Add Python to `references/DEPENDENCIES.md`.
6. Expand `references/EVAL.md` to 10 should-trigger and 10 should-not-trigger queries.
7. (Optional) Add `references/GLOSSARY.md` to make the skill a vocabulary building block as well as a conductor.

After these changes, run the trigger evals and a self-review with the updated `write-a-skill`.
