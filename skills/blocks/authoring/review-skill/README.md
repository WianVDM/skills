# review-skill

A model-invoked conductor that audits an existing skill against the skill standards, applies the review principles, and produces a verdict-led report or remediation plan.

## When to use

Use this skill when:

- The user wants to audit an existing skill without changing it.
- The user wants to refine or polish an existing skill.
- A conductor reaches the `change` branch and needs to review or update a skill.

## How to use

Invoke the skill by name, or let `write-a-skill` delegate the `change` branch to it.

The skill supports two gates:

- **review** — applies the review principles, runs a full audit, and produces a verdict-led audit report or an incomplete report.
- **update** — applies the review principles, produces a verdict-led audit report, a remediation plan, and applies changes after approval.

Before the rubric is scored, the conductor applies the review principles from `references/REVIEW_PRINCIPLES.md` (a fallback copy of `docs/skill-standards/reference/review-principles.md`). The verdict is always based on the full audit. If the core questions cannot be answered, the report is marked incomplete.

## Directory layout

```
review-skill/
├── SKILL.md
├── README.md
└── references/
    ├── DEPENDENCIES.md
    └── REVIEW_PRINCIPLES.md
└── evals/
    └── evals.json
```

## Key conventions

- **Conductor:** delegates evaluation to `audit-skill` and `validate-skill-frontmatter`.
- **Comprehend before critiquing:** applies the review principles before scoring the rubric.
- **Verdict-led:** the audit report leads with a verdict supported by findings.
- **Incomplete status:** reports are marked incomplete when core questions cannot be answered.
- **Read-only review:** the `review` gate does not modify files.
- **Approval gating:** the `update` gate applies changes only after explicit approval.
- **Context reports:** audit reports, incomplete reports, and remediation plans are written as context reports.
- **Final audit:** the `update` gate closes the loop with a final audit.

## Maintenance notes

- Update the workflow when the audit rubric or frontmatter schema changes.
- Keep the remediation plan format stable so consumers can parse it.
- Add near-miss triggers to `evals/evals.json` if new domains collide with this skill.
