---
skill: write-a-skill
version: "3.1"
timestamp: 2026-07-03T16:00:00Z
status: final
result: pass
---

# Self-audit: write-a-skill

**Overall verdict:** After the latest round of changes, `write-a-skill` fully aligns with the `skill-standards` fundamentals, the project target spec, and the recommendations from the standards review. No red findings remain.

## Summary of changes since last self-audit

- Added `disable-model-invocation: true` to `SKILL.md` frontmatter for unambiguous user-invocation.
- Replaced the redundant opening sentence with a load-bearing contract statement.
- Tightened the description to reduce duplication with `When to use`.
- Moved detailed branch workflows to `references/BRANCH_WORKFLOWS.md`, keeping `SKILL.md` at 145 lines.
- Added a one-line rationale for each branch in `SKILL.md`; the detailed phase rationales live in `references/BRANCH_WORKFLOWS.md`.
- Added Python 3.x to `references/DEPENDENCIES.md`.
- Expanded `references/EVAL.md` to 10 should-trigger and 10 should-not-trigger queries plus 10 behavioral evals.
- Added `references/GLOSSARY.md` as a shared vocabulary building block.
- Updated `skill-standards` docs (`04-structure.md`, `03-form-and-style.md`, `13-evaluation.md`) and the project target spec to clarify invocation frontmatter conventions and branch workflow disclosure.

## Checks

- [x] One core objective — single meta-conductor for skill lifecycle management.
- [x] Explicit out-of-scope — declared in `SKILL.md`.
- [x] Explicit dependencies — `references/DEPENDENCIES.md` lists required capabilities, including Python.
- [x] No secrets in files — none present.
- [x] Destructive actions confirmed — stated in user interaction rules and worker prompts.
- [x] Harness-agnostic and project-agnostic — no hardcoded harness or project specifics in core files.
- [x] No hidden assumptions — detection + confirmation is documented.
- [x] Appropriate skill type — conductor.
- [x] Form matches domain — conductor with clear steps and guidelines.
- [x] Steps have completion criteria — every branch ends with a completion criterion.
- [x] Description is trigger-rich and front-loads the leading word "Skill-design partner".
- [x] No duplicate triggers — each branch has a distinct trigger.
- [x] Leading word used — "Skill-design partner".
- [x] Negation pairs — positive directives accompany negative rules.
- [x] No vague guideline soup — every guideline is tied to a principle or concrete action.
- [x] No no-op lines — the opening sentence is now load-bearing; every line shapes behavior or points to a reference.
- [x] Progressive disclosure — branch details, schemas, and checklists live in `references/`.
- [x] State and reports documented — `references/STATE_SCHEMA.md` and `references/CONTEXT_REPORTS.md`.
- [x] Worker contract defined — `references/WORKER_CONTRACT.md` and all subagents reference it.
- [x] Scripts for deterministic logic — `scripts/detect-project-layout.py`.
- [x] Review cadence and evals planned — `references/EVAL.md` and `references/MAINTENANCE.md`.
- [x] Invocation mode declared — both `invocation: user-invoked` and `disable-model-invocation: true` in frontmatter.
- [x] Branch workflow disclosure — `SKILL.md` points to `references/BRANCH_WORKFLOWS.md`.
- [x] Glossary provided — `references/GLOSSARY.md` defines shared vocabulary.

## Yellow observations (non-blockers)

None after this round.

## Red findings

None.

## Blockers

None.

## Next action

Run the expanded behavioral evals in `references/EVAL.md` and iterate on any failures.
