---
name: review-skill
description: Audit an existing skill against the skill standards, produce a remediation plan, and optionally apply changes after explicit approval. Use when reviewing or updating a skill.
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [skill-review, audit, remediation, conductor, standards]
  verification_level: declared
  provenance:
    authored_by: mixed
    generated_by: agent
    origin: foreground
    reviewed_by: audit-skill
    reviewed_at: "2026-07-05T00:00:00Z"
    parent_session: write-a-skill-refactor
---

# review-skill

## Purpose

Audit an existing skill against the skill standards and, if requested, produce and apply a remediation plan after explicit approval.

## Type

Conductor.

## In scope

- Load the target skill files (`SKILL.md`, `README.md`, references, subagents, scripts, assets).
- Run `audit-skill` to evaluate against the rubric.
- Run `validate-skill-frontmatter` to check schema compliance.
- Produce a structured audit report as a context report.
- For the `update` gate, produce a remediation plan with concrete changes.
- For the `update` gate, apply changes only after explicit user approval for each change.
- For the `update` gate, run a final audit after changes.

## Out of scope

- This skill does not create new skills from scratch.
- It does not decide whether a capability should be a skill, script, MCP, or context file; use `decide-skill-shape` for that.
- It does not write or modify files in the `update` gate without explicit approval.

## When to use

- The user wants to audit an existing skill without changing it (`review` gate).
- The user wants to refine or polish an existing skill to follow the standards (`update` gate).
- A conductor (such as `write-a-skill`) reaches the `change` branch and needs to review or update a skill.

## Branch entry

Classify the user's intent into one gate. If unclear, ask one clarifying question with a proposed default.

| Gate | Trigger | Outcome |
|---|---|---|
| **review** | User wants to audit an existing skill without changing it. | Audit report only. |
| **update** | User wants to refine or polish an existing skill. | Audit → remediation plan → draft changes → confirm → final audit. |

**Completion criterion:** the gate is one of {review, update} and the user has confirmed or corrected the default.

## Workflow

### Review gate

1. **Read the skill.**
   - Load `SKILL.md`, `README.md`, and all files in `references/`, `subagents/`, `scripts/`, and `assets/`.
   - **Completion criterion:** all skill files are loaded.
2. **Run `audit-skill`.**
   - Evaluate the skill against the fundamentals rubric.
   - **Completion criterion:** audit report exists with findings and recommendations.
3. **Run `validate-skill-frontmatter`.**
   - Check frontmatter schema compliance.
   - **Completion criterion:** validation result is captured.
4. **Produce audit report.**
   - Write `{context}/skill-review/{skill-name}-audit.md` with summary, findings, and remediation plan.
   - **Completion criterion:** the audit report exists and references rubric criteria by ID.

### Update gate

1. **Read the skill.**
   - Load all skill files.
   - **Completion criterion:** all skill files are loaded.
2. **Run `audit-skill`.**
   - **Completion criterion:** audit report exists.
3. **Run `validate-skill-frontmatter`.**
   - **Completion criterion:** validation result is captured.
4. **Produce remediation plan.**
   - List concrete changes with effort estimates and rationale.
   - Write `{context}/skill-review/{skill-name}-remediation.md`.
   - **Completion criterion:** remediation plan exists.
5. **Confirm before applying.**
   - Present the plan; apply each change only after explicit approval.
   - **Completion criterion:** the user has approved or declined each proposed change.
6. **Apply approved changes.**
   - Write or edit files as approved.
   - **Completion criterion:** approved changes are applied.
7. **Run final audit.**
   - Close the loop and capture the result.
   - **Completion criterion:** final audit report exists.

## Output formats

### Audit report

```markdown
# Audit: {skill-name}

## Summary
- Blockers: N
- Warnings: N
- Suggestions: N
- Overall: PASS / FAIL

## Findings
| ID | Category | Severity | Check | Result | Recommendation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Remediation plan
- {finding ID}: {action to take}
```

### Remediation plan

```markdown
# Remediation plan: {skill-name}

## Changes
| # | Change | Rationale | Effort | Approved |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Open questions
- ...

## Blockers
- ...
```

## User interaction rules

- Ask one question at a time when the answer shapes the audit or remediation.
- Present recommendations, not just options.
- Confirm before any destructive action.
- Do not apply changes that are not explicitly approved.

## Security

- Prefer read-only inspection in the `review` gate.
- Do not write or overwrite files in the `update` gate without explicit approval.
- Do not install or run untrusted scripts from the skill under review.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `context-reports` skill — shared context-report conventions.
- `write-a-skill` — conductor for creating, reviewing, and updating skills.
