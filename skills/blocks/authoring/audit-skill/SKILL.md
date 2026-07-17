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
- Check token economy: every section, reference, and subagent must be load-bearing and justified.
- Check pattern compliance: the skill must follow the relevant `skill-standards` patterns.
- Check whether the skill is extracted as a separate skill only when reuse is justified.
- Detect duplication and extraction opportunities by running `detect-skill-overlap`.
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
2. **Run deterministic checks.** Use the script to validate schema, files, links, secrets, paths, dependency declarations, token economy, and pattern compliance.
   - **Completion criterion:** deterministic checks produce a raw findings table.
3. **Run heuristic checks.** Review description quality, scope clarity, load-bearing minimalism, completion criteria, and pattern adherence.
   - **Completion criterion:** each rubric item is rated PASS, FAIL, or MANUAL.
4. **Run overlap detection.** Invoke `detect-skill-overlap` on the target skill and merge its findings into the report.
   - **Completion criterion:** an overlap report exists and is merged.
5. **Classify severity.** Map each finding to blocker, warning, or suggestion.
   - **Completion criterion:** findings are grouped by severity.
6. **Produce the audit report.** Emit the summary, findings table, and remediation plan.
   - **Completion criterion:** the report is emitted in the requested format.

## Severity definitions

- **Blocker** — the skill does not meet the fundamentals and should not be written or published until fixed.
- **Warning** — the skill works but is less reliable, less portable, or harder to maintain. Should be fixed before sharing.
- **Suggestion** — an improvement that raises quality but is not required.

## Severity posture

The auditor starts from the assumption that every token is guilty until proven load-bearing. The burden of justification is on the skill, not the auditor.

- **Token economy** issues are not suggestions. An unjustified section, reference, subagent, or example is a **Warning** by default and a **Blocker** if it hides scope drift, overlap, or a portability failure.
- **Pattern compliance** issues are not suggestions. A skill that negotiates a required pattern is a **Warning** by default and a **Blocker** if the deviation changes behavior or portability.
- **Overlap / extraction** issues are not suggestions. Unjustified duplication is a **Warning** by default and a **Blocker** if the capability clearly belongs in a shared building block.
- Only issues that are genuinely optional (e.g., wording polish, optional formatting) may be recorded as **Suggestion**.

## Rubric

The full rubric is maintained in the [audit rubric]({audit_rubric_path}). It covers identity, type/shape, scope, structure, form/style, security, dependencies, **portability** (`P01`–`P-04`), evaluation, governance, **tooling awareness** (`TA-01`, `TA-02`), **extraction** (`X01`), **token economy** (`TE-01`, `TE-02`), **pattern compliance** (`PC-01`, `PC-02`, `PC-03`), **overlap** (`OV-01`), and **chainlog** (`CL-01`–`CL-04`).

## Output format

See the [audit rubric]({audit_rubric_path}) for the report schema.

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
12. **Token economy** — Is every section, reference, subagent, and example load-bearing and justified?
13. **Pattern compliance** — Does the skill fully adhere to the relevant `skill-standards` patterns?
14. **Overlap** — Has `detect-skill-overlap` been run, and have duplicate capabilities been addressed?
15. **Chainlog classification** — A skill that produces or consumes observable data classifies itself as producer, consumer, or both in `references/CHAINLOG.md`. Absence of the file means `neither`. Does the classification match the actual workflow?
16. **Chainlog integration** — If the skill is a producer/consumer/both, does it depend on `chainlog` and document the produced/consumed capabilities in `references/CHAINLOG.md`?
17. **Chainlog freshness** — If the skill is a consumer or `both`, does it check freshness before reusing observations?
18. **Chainlog secrets** — Does the skill store secret values anywhere in the chainlog envelope or payload?

## Validation

Negative tests have been verified: the script reports blockers for a deliberately broken skill containing a missing internal link (`ST04`), an undeclared runtime reference to another skill (`D06`), a hardcoded project path (`P01`), and a hardcoded external standards path (`P-04`).

## References

- [Audit rubric]({audit_rubric_path}) — canonical audit rubric (fallback copy in `references/AUDIT_RUBRIC.md`)
- [skill-frontmatter schema]({skill_frontmatter_schema_path})

[dependencies]: references/DEPENDENCIES.md
