# review-skill

A model-invoked conductor that audits an existing skill against the skill standards and optionally produces and applies a remediation plan.

## When to use

Use this skill when:

- The user wants to audit an existing skill without changing it.
- The user wants to refine or polish an existing skill.
- A conductor reaches the `change` branch and needs to review or update a skill.

## How to use

Invoke the skill by name, or let `write-a-skill` delegate the `change` branch to it.

The skill supports two gates:

- **review** — produces an audit report only.
- **update** — produces an audit report, a remediation plan, and applies changes after approval.

## Directory layout

```
review-skill/
├── SKILL.md
├── README.md
└── references/
    └── DEPENDENCIES.md
└── evals/
    └── evals.json
```

## Key conventions

- **Conductor:** delegates evaluation to `audit-skill` and `validate-skill-frontmatter`.
- **Read-only review:** the `review` gate does not modify files.
- **Approval gating:** the `update` gate applies changes only after explicit approval.
- **Context reports:** audit reports and remediation plans are written as context reports.
- **Final audit:** the `update` gate closes the loop with a final audit.

## Maintenance notes

- Update the workflow when the audit rubric or frontmatter schema changes.
- Keep the remediation plan format stable so consumers can parse it.
- Add near-miss triggers to `evals/evals.json` if new domains collide with this skill.
