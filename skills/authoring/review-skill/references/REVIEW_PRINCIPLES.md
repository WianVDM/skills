> This is a degraded fallback copy of `docs/skill-standards/reference/review-principles.md`. Prefer the canonical doc if available.

# Review principles

A skill review is a judgment, not a checklist. The reviewer applies the skill fundamentals to decide whether the skill is the right shape, the right scope, and the right token load.

## Core questions

Before scoring, answer:

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

## Severity posture

A reviewer starts from the assumption that every token is guilty until proven load-bearing. The skill author, not the reviewer, carries the burden of justification.

- **Token economy** issues are not suggestions. An unjustified section, reference, subagent, or example is a **Warning** by default and a **Blocker** if it hides scope drift or overlap.
- **Pattern adherence** issues are not suggestions. A skill that negotiates a required pattern is a **Warning** by default and a **Blocker** if the deviation changes behavior or portability.
- **Overlap / extraction** issues are not suggestions. Unjustified duplication is a **Warning** by default and a **Blocker** if the capability clearly belongs in a shared building block.
- Only issues that are genuinely optional (e.g., wording polish, optional formatting) may be recorded as **Suggestion**.

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
