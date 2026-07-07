# Governance, versioning, and maintenance

This file holds governance notes for human maintainers of `write-a-skill`. It does not shape runtime behavior; see `SKILL.md` for the operational contract.

## Maintenance and lifecycle

`write-a-skill` tracks its own changes because it is a shared conductor consumed by other skills and workflows. For skills produced by this conductor, `version` is optional unless the user requires it or the skill will be shared or consumed.

`write-a-skill` uses semantic versioning for its own lifecycle:

- **Major bump**: breaking changes to the skill interface, schema, or required capabilities.
- **Minor bump**: new branches, references, or significant backward-compatible workflow improvements.
- **Patch bump**: typo fixes, clarifications, or minor reference updates that do not change behavior.

Current version: **4.7.0**.

Bump the version when state/report schemas change, a new branch or major workflow step is added, subagent behavior changes significantly, or the audit rubric changes in a way that affects ratings. Do not bump for trivial wording fixes. For skills produced by this conductor, only suggest versioning if the user asks for it or if the skill will be distributed/consumed.

## Migration history

- **4.6.0 → 4.7.0**: added a pre-audit comprehension step to the `change` branch using the review principles in `docs/skill-standards/REVIEW_PRINCIPLES.md`; `review-skill` now produces a verdict-led audit report or an incomplete report. Updated the initialization routine to detect canonical standards via the configured `standards_path` and fall back to embedded references. No state migration required.
- **4.5.0 → 4.6.0**: extracted the `review` and `update` gates into a new `review-skill` conductor; declared it as a dependency and delegated the `change` branch in `BRANCH_WORKFLOWS.md` to it. No state migration required.
- **4.4.0 → 4.5.0**: extracted the `decide` gate into a new `decide-skill-shape` conductor; declared it as a dependency and delegated the `decide` gate in `BRANCH_WORKFLOWS.md` to it. No state migration required.
- **4.3.0 → 4.4.0**: extracted the shared `evals/evals.json` schema and evaluation conventions into a new `eval-format` vocabulary building block; declared it as a dependency and pointed `EVAL.md` to it. No state migration required.
- **4.2.0 → 4.3.0**: extracted shared context-report conventions (directory layout, envelope, freshness rules, and missing-report handling) into a new `context-reports` vocabulary building block; declared it as a dependency and pointed `STATE_SCHEMA.md` to it. No state migration required.
- **4.1.0 → 4.2.0**: extracted the shared subagent return contract into a new `worker-contract` vocabulary building block; declared it as a dependency and pointed `WORKER_CONTRACT.md` to it. No state migration required.
- **4.0.0 → 4.1.0**: collapsed the five-branch model into two top-level branches (`create` and `change`) with internal gates; updated `BRANCH_WORKFLOWS.md`, `EVAL.md`, and the `classify-intent` subagent to match. No state migration required.
- **3.1 → 4.0**: rewrote the conductor around a 10-phase workflow and five branches (`new`, `quick`, `update`, `review`, `decide`); delegated deterministic work to seven building-block skills; restructured references and contracts. No state migration required; the conductor starts fresh state files.

## Review cadence

- Review this skill after every 10 real-world uses or once per month, whichever comes first.
- Update the audit rubric when the `skill-standards` fundamentals change.
- Add a new eval to `references/EVAL.md` whenever a bug or surprising behavior is observed.
- Run the regression checklist in `references/EVAL.md` before merging any change.

## Maintenance checklist

Before releasing a new version:

- [ ] `SKILL.md` frontmatter version matches the version in this section (only if the skill is versioned).
- [ ] `README.md` reflects the current structure and conventions.
- [ ] All reference links in `SKILL.md` and `README.md` resolve.
- [ ] The audit rubric is still aligned with the target spec.
- [ ] Subagent prompts reference the correct standards and contracts.
- [ ] Trigger and behavioral evals pass.
- [ ] A self-review of `write-a-skill` shows no red principle findings.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on workflow and gates. Update the rubric in the `audit-skill` building block when standards change, and keep subagent personas narrow, explicit, and reusable.
