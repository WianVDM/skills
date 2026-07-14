# Governance, versioning, and maintenance

This file holds governance notes for human maintainers of `write-a-skill`. It does not shape runtime behavior; see `SKILL.md` for the operational contract.

## Maintenance and lifecycle

`write-a-skill` tracks its own changes because it is a shared conductor consumed by other skills and workflows. For skills produced by this conductor, `version` is optional unless the user requires it or the skill will be shared or consumed.

`write-a-skill` uses the versioning scheme defined in the project [`AGENTS.md`](../../../../AGENTS.md): all skills and artifacts start at **v1.0.0**, and increments are strictly right-to-left (v1.0.0 → v1.0.1 → ... → v1.0.9 → v1.1.0) with no semantic meaning assigned to major, minor, or patch. Bumps are based on the latest version published to GitHub, and each release bumps the version exactly once.

Current version: **v1.0.1**.

## Migration history

- **v1.0.0 → v1.0.1**: aligned `SKILL.md`, `skills.json`, and `GOVERNANCE.md` versions after the v4.7.0 reset; enforced canonical frontmatter by removing `metadata`/`author`/`tags` from the dependency closure and updating `audit-skill`, `parse-skill-frontmatter`, and `list-available-skills`. No state migration required.

### Pre-v1.0 history

Versions before v1.0.0 were a series of extractions and branch reorganizations under the old project numbering scheme. None required state migration:

- Extracted shared vocabulary building blocks (`worker-contract`, `context-reports`, `eval-format`) from monolithic guidance files.
- Extracted conductor skills (`decide-skill-shape`, `review-skill`) from inline `write-a-skill` branches.
- Collapsed the branch model into `create`/`change`, added pre-audit comprehension to the `change` branch, and added `standards_path` detection/fallback to initialization.
- Reset all versions to **v1.0.0** under the project-specific versioning scheme in `AGENTS.md`.

## Review cadence

- Review this skill after every 10 real-world uses or once per month, whichever comes first.
- Update the audit rubric when the `skill-standards` fundamentals change.
- Add a new eval to `references/EVAL.md` whenever a bug or surprising behavior is observed.
- Run the regression checklist in `references/EVAL.md` before merging any change.

## Maintenance checklist

Before releasing a new version, verify:

- The `SKILL.md` frontmatter version matches the version in this section (only if the skill is versioned).
- The `README.md` reflects the current structure and conventions.
- All reference links in `SKILL.md` and `README.md` resolve.
- The audit rubric is still aligned with the target spec.
- Subagent prompts reference the correct standards and contracts.
- Trigger and behavioral evals pass.
- A self-review of `write-a-skill` shows no red principle findings.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on workflow and gates. Update the rubric in the `audit-skill` building block when standards change, and keep subagent personas narrow, explicit, and reusable.
