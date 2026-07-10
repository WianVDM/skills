---
name: audit-skill
description: Check a skill against the skill fundamentals and report blockers, warnings, and suggestions with a structured remediation plan.
version: 1.0.1
invocation: model-invoked

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
- Check whether the skill is extracted as a separate skill only when reuse is justified.
- Produce a structured report with blocker/warning/suggestion severity.
- Provide a remediation plan for failed checks.

## Out of scope

- Modifying the skill being audited.
- Making value judgments about whether a skill is useful.
- Running behavioral evaluations (use `run-trigger-evals` for that).

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

The full rubric is maintained in `docs/skill-standards/reference/audit-rubric.md`. It covers identity, type/shape, scope, structure, form/style, security, dependencies, portability, evaluation, governance, **tooling awareness** (`TA-01`, `TA-02`), and **extraction** (`X01`).

## Output format

See `docs/skill-standards/reference/audit-rubric.md` for the report schema.

## Security

- The script is read-only. It does not write or modify the audited skill.
- It scans for secrets with regex patterns; it does not execute the skill.

## Dependencies

See [references/DEPENDENCIES.md][dependencies].

## Known limitations

- The script performs deterministic checks (schema validation, identity fields, files, links, secrets, hardcoded paths, dependency declarations, and confirmation wording). It cannot judge the quality of prose descriptions, scope clarity, or whether a completion criterion is truly observable. Those remain manual review items and appear as `MANUAL` in the findings table.
- The audit is read-only and does not execute the skill, so runtime behavioral correctness is out of scope.

## Manual review checklist

When the script reports `MANUAL` findings, use this checklist to complete the review:

1. **Description** — Does the first sentence front-load the skill's core action or domain?
2. **Triggers** — Does the description list distinct triggers, not synonyms?
3. **Type match** — Does the content match the declared skill type (building block, conductor, wrapper, multi-layer)?
4. **Scope clarity** — Is the objective one sentence? Do in-scope and out-of-scope lists contradict each other?
5. **Load-bearing prose** — Can any paragraph, example, or reference be removed without changing behavior?
6. **Completion criteria** — Does every step end with an observable completion criterion?
7. **Negation pairs** — Is every "do not X" paired with a "do Y"?
8. **Harness agnosticism** — Are there any hardcoded harness commands or product references?
9. **Confirmation gating** — Are destructive actions (writes, overwrites, deletes, installs) gated behind explicit approval?
10. **Failure mode** — Does the skill fail closed when a required tool, binary, or capability is missing?
11. **Extraction** — If this skill is a building block, is it cross-cutting, used by multiple skills, or solving a generic-domain problem? If it exists only to serve one other skill, should it be colocated?

## Validation

Negative tests have been verified: the script reports blockers for a deliberately broken skill containing a missing internal link (`ST04`), an undeclared runtime reference to another skill (`D06`), and a hardcoded project path (`P01`).

## References

- [Audit rubric][audit-rubric] — canonical audit rubric
- `docs/skill-standards/schemas/skill-frontmatter.schema.json`

[dependencies]: references/DEPENDENCIES.md
[audit-rubric]: ../../../../docs/skill-standards/reference/audit-rubric.md
