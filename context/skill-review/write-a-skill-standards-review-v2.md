---
report: standards-review
skill: write-a-skill
version: "3.1"
timestamp: 2026-07-03T17:00:00Z
status: final
reviewers: internal
standards: skill-standards package (G:/My Drive/.agents/docs/skill-standards)
inspiration: mattpocock/skills/skills/productivity/writing-great-skills
location: G:/My Drive/.agents/skills/write-a-skill
---

# Standards review: `write-a-skill` — workspace re-review

**Overall verdict:** The workspace copy at `G:/My Drive/.agents/skills/write-a-skill` is now identical to the updated global copy and passes the same standards review. All principle criteria are green; no blockers remain.

## Scope note

This review was run against the workspace copy of `write-a-skill` at `G:/My Drive/.agents/skills/write-a-skill`. The workspace copy was synchronized from the updated global copy and is now the source of truth for this project. The skill-standards package and the project target spec were already aligned in the previous step.

## Verification performed

- `diff -r` between the workspace copy and the updated global copy returned no differences.
- All markdown links in `SKILL.md` and `README.md` resolve.
- `SKILL.md` is 146 lines.
- `scripts/detect-project-layout.py` correctly detects the workspace layout from `G:/My Drive/.agents` with high confidence.

## Ratings (summary)

| Category | Rating | Key observation |
|---|---|---|
| A. Identity and invocation | 🟢 | `invocation: user-invoked` and `disable-model-invocation: true` both declared. |
| B. Objective and scope | 🟢 | One core objective, explicit out-of-scope. |
| C. Form and style | 🟢 | Branch rationales in `SKILL.md`; phase rationales in `BRANCH_WORKFLOWS.md`; completion criteria present. |
| D. Information hierarchy | 🟢 | `SKILL.md` is 146 lines; detailed workflows disclosed behind a pointer. |
| E. Global vs project-specific | 🟢 | No hardcoded paths; detection script + confirmation. |
| F. Configuration | 🟢/⚪ | N/A for the skill itself; config pattern documented for produced skills. |
| G. State and context | 🟢 | Schemas, resumption, and freshness documented. |
| H. Delegation and scripts | 🟢 | Subagents precise; Python dependency declared. |
| I. Reusability and composition | 🟢 | Rubric, worker contract, and glossary extracted. |
| J. Security | 🟢 | Secrets, destructive actions, untrusted projects addressed. |
| K. Evaluation and lifecycle | 🟢 | 10/10 trigger evals and 10 behavioral evals documented. |

## Full reports

For detailed findings and the previous comparison with Matt Pocock's `writing-great-skills`, see:

- `G:/My Drive/.agents/context/skill-review/write-a-skill-standards-review.md`
- `G:/My Drive/.agents/context/skill-review/write-a-skill-audit-v3.1.md`
- `G:/My Drive/.agents/context/skill-review/write-a-skill-self-audit-v3.1.md`

## Blockers

None.

## Recommended next action

Run the behavioral evals in `G:/My Drive/.agents/skills/write-a-skill/references/EVAL.md` from the workspace to confirm the skill behaves as expected in this project.
