# Review principles

A skill review is a judgment, not a checklist. The reviewer applies the skill fundamentals to decide whether the skill is the right shape, the right scope, and the right token load.

## Core questions

Before scoring, answer:

1. **Justify** — What single judgment does this skill make predictable? Would the agent be wrong without it?
2. **Shape** — Is this a skill, or should it be a script, MCP server, context file, or extension of an existing skill?
3. **Scope** — Is the objective one sentence? Are the boundaries explicit and non-overlapping?
4. **Prune** — Is every line load-bearing? Can a section, example, or reference be removed without changing behavior?
5. **Focus** — Does the phrasing produce the right result? Can leading words, negation pairs, or checkable completion criteria make it leaner?

## Verdict

After a full audit, lead the report with one verdict:

| Verdict | Meaning |
|---|---|
| **Keep** | The skill is sound. |
| **Prune** | The skill is sound but bloated; reduce token load. |
| **Reshape** | The skill is valid but the wrong shape or scope. |
| **Remove** | A non-skill solution is better. |

The verdict is a conclusion supported by the findings. It is not a substitute for the audit.

## Incomplete review

If the core questions cannot be answered, the report is **Incomplete**. It does not issue a verdict. It lists the open questions needed to complete the review.
