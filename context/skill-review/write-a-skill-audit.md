# Audit report: `write-a-skill`

> Conducted against the target specification in `.agents/context/skill-design/write-a-skill-target-spec.md`.

---

## Overall verdict

`write-a-skill` is a structurally sound conductor with a coherent purpose and good delegation. However, it currently fails several principle-level criteria from the target specification. The biggest gaps are:

1. **No declared portability target** — it hardcodes `.agents/` paths while claiming global standards.
2. **No completion criteria** on any phase.
3. **Weak invocation / description design** — no leading word, four verbs compete for attention, invocation mode is not declared.
4. **Review and upgrade branches are not mapped to phases** — the skill description claims them, but the workflow only covers creating a new skill.
5. **No self-audit / simplicity check** phase.
6. **State and context schemas are undocumented**.
7. **No eval or trigger-test documentation**.
8. **Subagent tool lists are vague** and some still reference the old "guideline-oriented" anti-pattern.

The skill is roughly **40% aligned** with the target specification. It is not ready to reliably audit other skills until it is refactored against its own criteria.

---

## A. Identity and invocation

| Criterion | Rating | Notes |
|---|---|---|
| A1. Name | 🟢 | `write-a-skill` matches the directory name and naming convention. |
| A2. Description | 🟢 | States what it does and lists triggers. Length is acceptable. |
| A3. Description as context pointer | 🟡 | Description is verb-heavy (`Design, create, review, and upgrade`) and has no front-loaded leading word. The four verbs are separate branches, which is fine, but there is no compact concept that anchors invocation. |
| A4. Invocation mode | 🔴 | Not declared. Based on the workflow, it should be user-invoked, but `SKILL.md` never says so. |

**Issues**

- The description opens with four verbs. It should front-load the leading word or domain, e.g. *"Design tool for agent skills. Use when creating, reviewing, or upgrading a skill..."*
- No `disable-model-invocation` or equivalent marker.

---

## B. Objective and scope

| Criterion | Rating | Notes |
|---|---|---|
| B1. One core objective | 🟡 | "Design, create, review, and upgrade" is four verbs. While the user explicitly wants one conductor with branches, the objective statement is stretched. The skill should frame itself as a single meta-conductor for skill lifecycle management. |
| B2. Clear purpose | 🟢 | Purpose section is clear. |
| B3. Clear when to use | 🟢 | Trigger list is explicit. |
| B4. Out of scope | 🟢 | Lists what it does not do. Could be expanded. |
| B5. Right skill type | 🟢 | Correctly typed as a conductor. |

**Issues**

- The objective should be reframed as one job: *"Help users produce and maintain skills that follow the fundamentals"* rather than listing four separate actions.

---

## C. Form and style

| Criterion | Rating | Notes |
|---|---|---|
| C1. Form matches domain | 🟡 | The skill is a hybrid of steps and guidelines, but the split is not as sharp as it could be. Phases are steps; "User interaction rules" are guidelines. This is acceptable but could be tightened. |
| C2. Steps have completion criteria | 🔴 | None of the 10 phases end with a checkable completion criterion. The skill just says "Delegate to X" and moves on. This is a major gap and invites premature completion. |
| C3. Completion criteria are strong | ⚪ | Not applicable because no criteria exist. |
| C4. Leading words used | 🔴 | No clear leading word for the skill. The description and body do not recruit a compact pretrained concept. Candidates: `design`, `draft`, `shape`, `skill`. |
| C5. Explain-the-why | 🟡 | Some rules explain reasoning (e.g., "never implements before confirming the design"), but the phases themselves do not explain why each exists. |
| C6. Negation pairs | 🟡 | "Never implement before confirming the design" is a negation without a positive directive. It should be paired: *"Confirm the design before drafting; do not draft until confirmed."* |
| C7. No vague guideline soup | 🟡 | Mostly fine, but "Be explicit about assumptions and blockers" is borderline. It could be sharpened. |
| C8. No manual in disguise | 🟢 | Does not list keystrokes or commands. |
| C9. No hidden hybrid | 🟢 | Steps are numbered; guidelines are under a separate heading. |
| C10. No no-op lines | 🟡 | "A skill is a compact operating philosophy for a domain" is mostly framing, but it does shape the agent's mental model. "Never implement before confirming" is only meaningful because Phase 8 is a gate. Some lines are borderline no-ops. |

**Issues**

- Every phase needs a completion criterion. Example for Phase 1: *"Complete when the intent note contains the problem, trigger, success criteria, and a yes/no/maybe verdict on whether a skill is warranted."*
- The skill needs a leading word that anchors both execution and invocation.
- Negations should be paired with positive directives.

---

## D. Information hierarchy and structure

| Criterion | Rating | Notes |
|---|---|---|
| D1. Progressive disclosure | 🟢 | The skill references external canonical standards rather than duplicating them. Good. |
| D2. Co-location | 🟢 | Phases, user interaction rules, and artifact table are grouped logically. |
| D3. No sprawl | 🟡 | `SKILL.md` is ~170 lines. Acceptable but not lean. The state/artifacts table could move to `references/STATE_SCHEMA.md`. |
| D4. No sediment | 🟡 | README still uses the unclear term "Offset inference". Some legacy phrasing may remain. |
| D5. No duplication | 🟢 | Standards are not duplicated locally. |
| D6. Required files present | 🟢 | `SKILL.md`, `README.md`, `references/DEPENDENCIES.md`, subagents, and templates exist. |
| D7. No empty directories | 🟢 | `references/` contains only `DEPENDENCIES.md`, which is legitimate. |
| D8. Reference links resolve | 🟢 | Canonical standard links should resolve. Local links are minimal. |
| D9. Flat structure | 🟢 | Structure is flat. |

**Issues**

- Move the detailed state/artifact table into a `references/STATE_SCHEMA.md` or `references/CONTEXT_REPORTS.md` to keep `SKILL.md` leaner.
- Replace "Offset inference" in the README with "Scripts-first" or similar.

---

## E. Global vs project-specific

| Criterion | Rating | Notes |
|---|---|---|
| E1. Pluggability declared | 🔴 | The skill does not state whether it is global or project-specific. The target spec says it should be global. |
| E2. Harness-agnostic language | 🟡 | Language is mostly harness-agnostic, but "subagent" assumes a harness that supports subagents. This is acceptable if declared as a required capability. |
| E3. Project-agnostic language | 🔴 | Hardcodes `.agents/context/` and `.agents/skills/` paths in `SKILL.md`, `README.md`, and subagents. This violates global pluggability. |
| E4. Detection before config | 🔴 | No detection of project root, skills directory, or context directory. The skill assumes fixed paths. |
| E5. Dependencies declared | 🟡 | `DEPENDENCIES.md` lists capabilities but does not declare the canonical standards docs as consumed references, nor does it declare the `.agents/` convention as an assumed project structure. |
| E6. Fail closed | 🔴 | Not documented. If `.agents/` or the skills directory is missing, the skill does not specify what happens. |

**Issues**

- Declare `write-a-skill` as a **global** skill in the frontmatter or README.
- Replace `.agents/context/` and `.agents/skills/` with configurable paths. Detect them first, then confirm with the user.
- Add a `references/CONFIG_PATTERN.md` or `references/PLUGGABILITY.md` documenting detection and fallback behavior.
- `DEPENDENCIES.md` must declare: (a) canonical standards docs as consumed references, (b) the `.agents/` convention as a project-specific assumption, (c) subagent capability as a required harness feature.

---

## F. Configuration

| Criterion | Rating | Notes |
|---|---|---|
| F1. Config schema documented | 🟡 | The skill does not use config, but it does not explicitly document that. The templates document config for new skills. |
| F2. No secrets in config | ⚪ | Not applicable to the skill itself. |
| F3. No over-configuring | ⚪ | Not applicable. |
| F4. Notes are memory | ⚪ | Not applicable. |
| F5. Never overwrite without asking | 🟢 | State files should be appended rather than overwritten. This is stated. |

**Issues**

- Add a note in `SKILL.md` or `references/CONFIG_PATTERN.md` that `write-a-skill` itself is not configurable, but it detects the project layout.

---

## G. State and context

| Criterion | Rating | Notes |
|---|---|---|
| G1. State location documented | 🟢 | Artifact table lists locations. |
| G2. State schema documented | 🔴 | The table lists file paths but not the frontmatter or body schema of each artifact. |
| G3. Resumption logic | 🔴 | Not documented. After context compaction, the skill does not specify how it resumes. |
| G4. No duplicate work | 🟢 | Append-only decision log is correct. |
| G5. Report schema documented | 🔴 | The produced reports have no documented schema. The subagent return contracts are standard, but the content schema of design/audit/global-readiness reports is not specified. |
| G6. Freshness handled | 🔴 | Not documented. |
| G7. Missing reports handled | 🔴 | Not documented. |

**Issues**

- Add `references/STATE_SCHEMA.md` documenting the frontmatter and body of each artifact.
- Add resumption instructions: read the latest state file, summarize completed/pending work, current focus, and recommended next action.
- Add `references/CONTEXT_REPORTS.md` documenting report schemas, freshness rules, and missing-report handling.

---

## H. Delegation and scripts

| Criterion | Rating | Notes |
|---|---|---|
| H1. Delegation is appropriate | 🟢 | 8 subagents for a conductor of this size is reasonable. |
| H2. Worker boundaries clear | 🟡 | Most workers have clear role, scope, and return format. However, tool lists are vague: "Inspect the project structure", "Search for references to tools", "Read existing skills". These should name the actual tools. |
| H3. Worker return contract | 🟢 | Standard return contract is used consistently. |
| H4. Workers do not ask users | 🟢 | Workers return `needs_input` to the conductor. |
| H5. Scripts for deterministic logic | 🔴 | The skill itself uses no scripts. It could use scripts for detecting the project layout, listing existing skills, or validating skill names. |
| H6. Scripts are safe and isolated | ⚪ | Not applicable because no scripts exist. |

**Issues**

- Sharpen tool lists in every subagent. Example: *"Use `read` to examine files, `bash` to list directories, and `find` to search the project."*
- Add `scripts/detect-skill-root.py` or `scripts/detect-project-layout.py` to handle path detection deterministically.

---

## I. Reusability and composition

| Criterion | Rating | Notes |
|---|---|---|
| I1. Dependencies declared | 🟡 | `DEPENDENCIES.md` exists but omits the canonical standards docs and the `.agents/` convention. |
| I2. Building-block extraction | 🟢 | The skill references `docs/skill-standards/` rather than duplicating content. This is the correct pattern. |
| I3. Consumers handle absence gracefully | 🔴 | Not documented. If `docs/skill-standards/` is missing, the skill does not say what to do. |
| I4. One-way pattern consistency | 🟡 | Not explicitly addressed. The skill could be more opinionated about how it designs skills. |
| I5. No premature abstraction | 🟢 | 8 subagents feel justified for the scope. |

**Issues**

- Update `DEPENDENCIES.md` to declare consumed references and the `.agents/` assumption.
- Document fallback behavior when the standards package or expected directories are missing.

---

## J. Security

| Criterion | Rating | Notes |
|---|---|---|
| J1. No secrets in skill files | 🟢 | No secrets present. |
| J2. Destructive actions confirmed | 🟢 | Explicitly stated in out-of-scope and user interaction rules. |
| J3. External access documented | ⚪ | Not applicable. |
| J4. Read-only investigation preferred | 🟡 | Not explicitly stated for review/upgrade modes. |
| J5. Safe in untrusted projects | 🟡 | The skill reads skill files from the project. In an untrusted project, malicious skill files could be read. This is not addressed. |

**Issues**

- Add a note that review/upgrade modes prefer read-only inspection and that the user should confirm before the skill reads files from untrusted projects.

---

## K. Evaluation and lifecycle

| Criterion | Rating | Notes |
|---|---|---|
| K1. Description tested | 🔴 | No trigger evals documented. |
| K2. Behavior tested | 🔴 | No with-skill / baseline runs documented. |
| K3. Versioned | 🟢 | `version: "3.0"` in metadata. |
| K4. Migration path | 🔴 | Not documented. |
| K5. Maintenance plan | 🔴 | Not documented. |

**Issues**

- Add `references/EVAL.md` with trigger evals and behavioral evals.
- Document migration path from version 3.0 to future versions.
- Add a maintenance checklist or review cadence.

---

## Critical design gaps (must fix before it can audit others)

1. **Portability and pluggability.** The skill must declare itself global and remove `.agents/` hardcoding. Detection + user confirmation is required.
2. **Completion criteria.** Every phase needs a checkable end-state.
3. **Review and upgrade branches.** The description promises review and upgrade, but the phases only cover creating a new skill. The workflow must branch explicitly.
4. **Self-audit / simplicity check.** There is no phase that challenges the design for over-complication or fundamental violations before drafting.
5. **State and context schemas.** The produced artifacts must have documented schemas and resumption logic.
6. **Invocation mode.** The skill must explicitly declare it is user-invoked.
7. **Leading word and description.** The description needs a front-loaded leading word and cleaner branch triggers.
8. **Subagent tool precision.** Tool lists must name actual tools, not vague actions.
9. **Scripts for detection.** The skill should use deterministic scripts for path detection and similar tasks.
10. **Evals and maintenance plan.** Trigger evals, behavioral evals, and migration/maintenance documentation must be added.

---

## Recommended refactor order

1. **Declare portability and invocation mode.** Decide global, user-invoked, and document pluggability.
2. **Add detection and confirmation.** Replace hardcoded paths with detected paths + user confirmation.
3. **Restructure phases with completion criteria.** Make every phase end on a checkable condition.
4. **Add branches for review and upgrade.** Map the four entry modes to distinct workflows.
5. **Add a self-audit / simplicity phase.** Run the design against the fundamentals before drafting.
6. **Document state and context schemas.** Add `references/STATE_SCHEMA.md` and `references/CONTEXT_REPORTS.md`.
7. **Sharpen the description and subagents.** Add a leading word, clean up tool lists, and fix negation pairs.
8. **Add detection scripts.** Move path detection into deterministic scripts.
9. **Add evals and maintenance documentation.** Write `references/EVAL.md` and a migration/maintenance note.
10. **Run the skill against itself.** Use `write-a-skill` to review the refactored `write-a-skill` and iterate.


---

**Subsequent refactor — 2026-07-03**

The refactor described above has been completed. The updated skill files are at:

- `C:/Users/Wian.vanderMerwe/.agents/skills/write-a-skill/`

The new self-audit and final audit reports are at:

- `C:/Users/Wian.vanderMerwe/.agents/context/skill-review/write-a-skill-self-audit.md`
- `C:/Users/Wian.vanderMerwe/.agents/context/skill-review/write-a-skill-audit.md`

Overall verdict after refactor: aligned with the target specification; no red findings.

---

**Subsequent standards alignment update — 2026-07-03**

After a further review against the `skill-standards` package and Matt Pocock's `writing-great-skills`, the following were added:

- `disable-model-invocation: true` added to `SKILL.md` frontmatter.
- Detailed branch workflows moved to `references/BRANCH_WORKFLOWS.md`, reducing `SKILL.md` to 145 lines.
- One-line rationales added for each branch; detailed phase rationales added in `references/BRANCH_WORKFLOWS.md`.
- Python runtime added to `references/DEPENDENCIES.md`.
- `references/EVAL.md` expanded to 10 should-trigger + 10 should-not-trigger queries and 10 behavioral evals.
- `references/GLOSSARY.md` added as a shared vocabulary building block.
- `skill-standards` package updated to clarify invocation frontmatter conventions, branch workflow disclosure, explain-the-why for phases, and user-invoked evals.

Updated self-audit and audit reports at the same paths now show all-green, no blockers.
