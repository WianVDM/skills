---
name: audit-skill
description: Check a skill against the skill fundamentals and report blockers, warnings, and suggestions with a structured remediation plan.
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [audit, review, standards, building-block]
  verification_level: declared
---

# audit-skill

## Purpose

Evaluate a skill directory or `SKILL.md` against the skill fundamentals and produce a structured audit report with actionable findings.

## Type

Building block.

## In scope

- Validate frontmatter identity fields and schema compliance.
- Check file existence and internal link integrity.
- Check for secrets, hardcoded paths, and harness-specific product references.
- Verify dependency declarations and destructive-action confirmation.
- Check scope clarity, type/shape consistency, and portability.
- Produce a structured report with blocker/warning/suggestion severity.
- Provide a remediation plan for failed checks.

## Out of scope

- Modifying the skill being audited.
- Making value judgments about whether a skill is useful.
- Running behavioral evaluations (use `run-trigger-evals` for that).
- Full frontmatter schema validation (use `validate-skill-frontmatter` for that).

## When to use

- A skill author wants to review a skill before publishing or sharing it.
- A conductor needs to validate a draft before writing files.
- A CI pipeline needs to enforce standards compliance.

## Steps

1. **Accept the skill path or `SKILL.md` content.**
   - **Completion criterion:** the target skill is identified and readable.
2. **Run deterministic checks.** Use the script to validate schema, files, links, secrets, paths, and dependency declarations.
   - **Completion criterion:** deterministic checks produce a raw findings table.
3. **Run heuristic checks.** Review description quality, scope clarity, load-bearing minimalism, and completion criteria.
   - **Completion criterion:** each rubric item is rated PASS, FAIL, or MANUAL.
4. **Classify severity.** Map each finding to blocker, warning, or suggestion.
   - **Completion criterion:** findings are grouped by severity.
5. **Produce the audit report.** Emit the summary, findings table, and remediation plan.
   - **Completion criterion:** the report is emitted in the requested format.

## Severity definitions

- **Blocker** — the skill does not meet the fundamentals and should not be written or published until fixed.
- **Warning** — the skill works but is less reliable, less portable, or harder to maintain. Should be fixed before sharing.
- **Suggestion** — an improvement that raises quality but is not required.

## Rubric

The full rubric is maintained in `docs/skill-standards/AUDIT_RUBRIC.md`. It covers identity, type/shape, scope, structure, form/style, security, dependencies, portability, evaluation, and governance.

## Output format

See `docs/skill-standards/AUDIT_RUBRIC.md` for the report schema.

## Security

- The script is read-only. It does not write or modify the audited skill.
- It scans for secrets with regex patterns; it does not execute the skill.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `docs/skill-standards/AUDIT_RUBRIC.md` — canonical audit rubric
- `docs/skill-standards/schemas/skill-frontmatter.schema.json`
