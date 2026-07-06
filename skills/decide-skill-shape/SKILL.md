---
name: decide-skill-shape
description: Help decide whether a problem should be solved by a new skill, an existing skill, a script, an MCP server, a context file, or a mode. Use when the user is unsure what shape to build, or when a conductor needs a shape recommendation.
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [skill-design, shape, decision, conductor]
  verification_level: declared
depends:
  - list-available-skills
---

# decide-skill-shape

## Purpose

Help the user choose the right shape for a capability: a new skill, an existing skill, a script, an MCP server, a context file, or a mode.

## Type

Conductor.

## In scope

- Capture the problem in one or two sentences.
- Explore existing skills and registry results that might cover the problem.
- Ask classification questions to narrow the shape.
- Apply decision rules to recommend a shape.
- Present the recommendation, alternatives, and trade-offs.
- Write a decision report as a context report.

## Out of scope

- This skill does not write the final skill, script, or MCP server; it only recommends the shape.
- It does not install or modify skills without explicit approval.
- It does not replace the user's judgment; the user confirms or rejects the recommendation.

## When to use

- The user asks "Should this be a skill, script, MCP, or context file?"
- The user has a problem but does not know what shape to build.
- A conductor (such as `write-a-skill`) reaches the `decide` gate and needs a shape recommendation.

## Steps

1. **Capture the problem.**
   - Ask the user to describe the task in one or two sentences if it is not already clear.
   - **Completion criterion:** a problem statement exists in the decision report or intent note.
2. **Explore existing solutions.**
   - Run `list-available-skills` to discover local skills.
   - Optionally run `search-skills-registry` to find third-party skills.
   - **Completion criterion:** an alternatives report exists listing existing skills and registry results.
3. **Classify the problem.**
   - Ask one question at a time when the answer shapes the recommendation:
     - Is this a repeated, judgment-shaped task?
     - Should it fire autonomously, or only when explicitly invoked?
     - Does it coordinate multiple tools or skills?
     - Is it always-on guidance, or on-demand?
     - Is the output a deterministic transformation, or domain-shaped judgment?
     - Is it tied to a specific framework or convention?
   - **Completion criterion:** classification answers are recorded.
4. **Apply decision rules.**
   - Use the decision table in [references/DECISION_RULES.md](references/DECISION_RULES.md).
   - **Completion criterion:** a primary shape is recommended with rationale.
5. **Present recommendation.**
   - Explain the primary recommendation, alternatives, and trade-offs.
   - Propose a default and ask the user to confirm, reject, or request more options.
   - **Completion criterion:** the user has confirmed, rejected, or asked for more options.
6. **Write decision report.**
   - Write the report to `{context}/decide-skill-shape/{key}-decision-report.md`.
   - **Completion criterion:** the decision report exists with problem summary, recommendation, rationale, alternatives, and suggested next step.

## Output format

A decision report with the following structure:

```markdown
# Decision report: {topic}

## Problem summary
...

## Recommendation
{skill | script | MCP server | context file | mode | reuse existing skill}

## Rationale
...

## Alternatives considered
- ...

## Suggested next action
- ...
```

## Decision rules

For the full decision table, see [references/DECISION_RULES.md](references/DECISION_RULES.md). At a high level:

- Choose a **new skill** when the task is repeated, judgment-shaped, and reusable across projects.
- Choose an **existing skill** when the problem is already covered.
- Choose a **script** when the output is deterministic and the task is narrow.
- Choose an **MCP server** when the task needs external tooling or real-time data.
- Choose a **context file** when the task is reference or configuration, not behavior.
- Choose a **mode** when the task is always-on guidance or a persistent persona.

## User interaction rules

- Ask one question at a time when the answer shapes the recommendation.
- Present recommendations, not just options.
- Confirm before any destructive action.
- Do not choose on the user's behalf without first exploring alternatives.

## Security

- Prefer read-only inspection when exploring alternatives.
- Do not install or modify skills without explicit approval.
- Do not write files other than the decision report unless explicitly authorized.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Decision rules](references/DECISION_RULES.md)
- `context-reports` skill — shared context-report conventions.
- `write-a-skill` — conductor for creating, reviewing, and updating skills.
