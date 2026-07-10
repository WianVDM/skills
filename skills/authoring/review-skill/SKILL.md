---
name: review-skill
description: Audit an existing skill against the skill standards, apply the review principles, and produce a verdict-led report or remediation plan after explicit approval. Use when reviewing or updating a skill.
version: 1.0.1
invocation: model-invoked
depends:
  - audit-skill
  - validate-skill-frontmatter
  - detect-skill-overlap
---

# review-skill

## Purpose

Audit an existing skill against the skill standards, apply the review principles to understand it, and produce a verdict-led report or remediation plan after explicit approval. If the core questions cannot be answered, produce an incomplete report instead of a verdict.

## Type

Conductor.

## In scope

- Load the target skill files (`SKILL.md`, `README.md`, references, subagents, scripts, assets) and the full dependency closure.
- Apply the review principles from `references/REVIEW_PRINCIPLES.md` (a fallback copy of `docs/skill-standards/reference/review-principles.md`) before scoring the rubric.
- Check token economy: every section, reference, and subagent must be justified.
- Check pattern adherence: the skill must follow the relevant `skill-standards` patterns with no wiggle room.
- Run `detect-skill-overlap` to identify duplication and extraction opportunities.
- Run `audit-skill` to evaluate against the rubric.
- Run `validate-skill-frontmatter` to check schema compliance.
- Issue a verdict only after a full audit.
- Lead the audit report with a verdict.
- Produce an incomplete report when the core questions cannot be answered.
- Produce a structured audit report as a context report.
- For the `update` gate, produce a remediation plan with concrete changes.
- For the `update` gate, apply changes only after explicit user approval for each change.
- For the `update` gate, run a final audit after changes.

## Out of scope

- This skill does not create new skills from scratch.
- It does not issue a verdict without first running a full audit.
- It does not guess at a verdict when information is missing.
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
| **review** | User wants to audit an existing skill without changing it. | Verdict-led audit report, or incomplete report. |
| **update** | User wants to refine or polish an existing skill. | Verdict-led audit report → remediation plan → draft changes → confirm → final audit. |

**Completion criterion:** the gate is one of {review, update} and the user has confirmed or corrected the default.

## Workflow

Both gates share the same comprehension and audit phase. The `update` gate adds a remediation phase after the verdict.

### Shared comprehension and audit phase

1. **Read the skill.**
   - Load `SKILL.md`, `README.md`, and all files in `references/`, `subagents/`, `scripts/`, and `assets/`.
   - **Completion criterion:** all skill files are loaded.
2. **Comprehend the skill.**
   - Apply the review principles from `references/REVIEW_PRINCIPLES.md` (a fallback copy of `docs/skill-standards/reference/review-principles.md`).
   - Answer the eleven core questions and record the answers.
   - **Completion criterion:** the eleven core questions are answered, or the missing information is documented.
3. **Run overlap detection.**
   - Run `detect-skill-overlap` on the target skill.
   - If the skill is unavailable, document the degraded review and warn the user that overlap detection is missing.
   - **Completion criterion:** an overlap report exists or its absence is documented.
4. **Produce an incomplete report if necessary.**
   - If the core questions cannot be answered, write `{context}/skill-review/{skill-name}-incomplete.md` with open questions and stop.
   - **Completion criterion:** incomplete report exists and no verdict is issued.
5. **Run `audit-skill`.**
   - Evaluate the skill against the fundamentals rubric.
   - **Completion criterion:** audit report exists with findings and recommendations.
6. **Run `validate-skill-frontmatter`.**
   - Check frontmatter schema compliance.
   - **Completion criterion:** validation result is captured.

### Review gate outcome

6. **Produce a verdict-led audit report.**
   - Write `{context}/skill-review/{skill-name}-audit.md`.
   - Lead with the verdict, then findings, then remediation plan.
   - **Completion criterion:** the report exists, references rubric criteria by ID, and includes a verdict supported by findings.

### Update gate outcome

6. **Produce remediation plan.**
   - List concrete changes with effort estimates and rationale, informed by the comprehension step and verdict.
   - Write `{context}/skill-review/{skill-name}-remediation.md`.
   - **Completion criterion:** remediation plan exists.
7. **Confirm before applying.**
   - Present the plan; apply each change only after explicit approval.
   - **Completion criterion:** the user has approved or declined each proposed change.
8. **Apply approved changes.**
   - Write or edit files as approved.
   - **Completion criterion:** approved changes are applied.
9. **Run final audit.**
   - Close the loop and capture the result.
   - **Completion criterion:** final audit report exists.

## Core question checklist

Before scoring, answer and record the eleven core questions from `references/REVIEW_PRINCIPLES.md`:

1. **Justify** — What single judgment does this skill make predictable? Would the agent be wrong without it?
2. **Shape** — Is this a skill, or should it be a script, MCP server, context file, or extension of an existing skill?
3. **Scope** — Is the objective one sentence? Are the boundaries explicit and non-overlapping?
4. **Prune** — Is every line load-bearing? Can a section, example, or reference be removed without changing behavior?
5. **Focus** — Does the phrasing produce the right result? Can leading words, negation pairs, or checkable completion criteria make it leaner?
6. **Dependencies** — Are required dependencies checked eagerly and recommended/optional dependencies evaluated lazily when the skill has multiple methods or branches? Is the full dependency surface still declared?
7. **Tooling awareness** — Does the skill name capabilities before tools? Does it detect available tools, prefer the best one, and disclose degraded sources?
8. **Contain** — Should this capability be colocated inside an existing skill, or is extraction into a separate skill justified by reuse?
9. **Token economy** — Is every token justified? What would break if this section, reference, subagent, or example were removed?
10. **Pattern adherence** — Does the skill fully adhere to the relevant `skill-standards` patterns with no wiggle room?
11. **Overlap / extraction** — Does this skill overlap with an existing building block? Could any part be adapted to work generically with any skill?

If any question cannot be answered, produce an incomplete report instead of a verdict.

## Verdict guidance

The verdict is always one of: **Keep**, **Prune**, **Reshape**, or **Remove**. No other verdict is valid.

| Verdict | Use when |
|---|---|
| **Keep** | The skill is sound, focused, and adheres to the patterns. |
| **Prune** | The skill is sound but contains unjustified tokens, sediment, or bloat; reduce token load before publishing. |
| **Reshape** | The skill is valid but the wrong shape, scope, or pattern adherence; it may need to be split, merged, or retyped. |
| **Remove** | The skill duplicates an existing building block or a non-skill solution is better. |

Apply these rules when choosing a verdict:

- If the audit shows unresolved blockers, the verdict is not **Keep**.
- If **Token economy** is weak, lean toward **Prune**.
- If **Pattern adherence** is missing or the **Shape** / **Scope** is wrong, lean toward **Reshape**.
- If **Overlap / extraction** shows the skill duplicates an existing building block without adding distinct value, lean toward **Remove**.
- If the skill contains a capability that should be extracted as a generic building block, lean toward **Reshape** (split the skill) unless the extraction itself is the recommended remediation.

## Output formats

### Verdict-led audit report

```markdown
# Review: {skill-name}

## Verdict
{Keep / Prune / Reshape / Remove} — one-sentence rationale.

## Findings
| ID | Category | Severity | Check | Result | Recommendation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Remediation plan
- {finding ID}: {action to take}
```

### Incomplete report

Use this format when the core questions cannot be answered. An incomplete report does not issue a verdict.

```markdown
# Review (incomplete): {skill-name}

## Open questions
- {core question}: {what is missing}
- {core question}: {what is missing}
```

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

See [references/DEPENDENCIES.md][dependencies].

## References

- [Review principles][review-principles] — fallback copy of `docs/skill-standards/reference/review-principles.md`.

[dependencies]: references/DEPENDENCIES.md
[review-principles]: references/REVIEW_PRINCIPLES.md
- `context-reports` skill — shared context-report conventions.
- `write-a-skill` — conductor for creating, reviewing, and updating skills.
