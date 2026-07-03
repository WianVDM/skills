# Maintenance and versioning

This document describes how `write-a-skill` is maintained, how versions are bumped, and how breaking changes are handled.

## Version policy

`write-a-skill` uses semantic versioning for its own lifecycle:

- **Major bump** (e.g., `3.x` → `4.0`): breaking changes to the skill interface, schema, or required capabilities.
- **Minor bump** (e.g., `3.0` → `3.1`): new branches, new references, or significant workflow improvements that are backward compatible.
- **Patch bump** (e.g., `3.1.0` → `3.1.1`): typo fixes, clarifications, or minor reference updates that do not change behavior.

Current version: **3.1**.

## What triggers a version bump

Bump the version when:

- The schema of state artifacts or reports changes.
- A new branch or major workflow step is added.
- Subagent behavior changes significantly.
- The audit rubric changes in a way that affects ratings.
- Required capabilities or dependencies change.

Do not bump the version for trivial wording fixes unless they change how the skill behaves.

## Migration path

When a breaking change is introduced, document in this section:

- What changed and why.
- How stale state artifacts or reports should be handled.
- Any manual steps a user must take to migrate.

### 3.0 → 3.1

- Added explicit `invocation: user-invoked` and `scope: global` declarations.
- Replaced hardcoded `.agents/` paths with `scripts/detect-project-layout.py` + user confirmation.
- Split the single workflow into four branches: New, Quick, Review, Upgrade.
- Added completion criteria to every phase.
- Added self-audit phase and anti-over-complication checks.
- Added documented schemas for state artifacts, context reports, and worker returns.
- Replaced guideline-oriented references with a single `references/AUDIT_RUBRIC.md`.
- Added eval and maintenance documentation.

No migration is required for state artifacts from 3.0; they are no longer used by the new workflow. Old artifact paths may still be read for historical context, but the conductor should start fresh state files for new engagements.

## Review cadence

- Review this skill after every 10 real-world uses or once per month, whichever comes first.
- Update the rubric when the `skill-standards` fundamentals change.
- Add a new eval to `references/EVAL.md` whenever a bug or surprising behavior is observed.
- Run the regression checklist in `references/EVAL.md` before merging any change.

## Maintenance checklist

Before releasing a new version:

- [ ] `SKILL.md` frontmatter version is updated.
- [ ] `README.md` reflects the current structure and conventions.
- [ ] All reference links in `SKILL.md` and `README.md` resolve.
- [ ] The audit rubric is still aligned with the target spec.
- [ ] Subagent prompts reference the correct standards and contracts.
- [ ] The detection script is still deterministic and safe.
- [ ] Trigger and behavioral evals pass.
- [ ] A self-review of `write-a-skill` shows no red principle findings.
