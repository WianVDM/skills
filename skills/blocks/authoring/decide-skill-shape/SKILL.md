---
name: decide-skill-shape
description: Help decide whether a problem should be solved by a new skill, an existing skill, a script, an MCP server, a context file, or a mode. Use when the user is unsure what shape to build, or when a conductor needs a shape recommendation.
version: 1.0.1
invocation: model-invoked
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
- Consume an overlap findings report from `detect-skill-overlap` when provided by the caller (e.g., `write-a-skill`'s `decide` gate), using it to identify existing capabilities and extraction opportunities.
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
   - If the caller provides an overlap findings report from `detect-skill-overlap`, use it to identify:
     - Existing skills that already implement the capability.
     - Capabilities that could be extracted as a generic building block.
     - Reuse / colocate / extract options for any significant overlap.
   - Also consider whether an existing tool, MCP server, native binary, or context file already fulfills the capability before building a new skill.
   - **Completion criterion:** an alternatives report exists listing existing skills, tool categories, registry results, and any overlap findings.
3. **Classify the problem.**
   - Ask one question at a time when the answer shapes the recommendation:
     - Is this a repeated, judgment-shaped task or a narrow, deterministic transformation?
     - Should it fire autonomously, only when explicitly invoked, or always be active?
     - Does it coordinate multiple tools or skills, or is it a single focused capability?
     - Does this capability belong inside an existing skill, or is extraction as a separate skill justified by reuse?
       - Use the overlap findings report (if available) to answer this: if the capability already exists in two or more skills under the same category, extraction is a strong candidate; if only one skill uses it, colocation is usually preferred.
     - Is the output behavior, reference/configuration, or external tooling?
   - **Completion criterion:** classification answers are recorded.
4. **Apply decision rules.**
   - Use the decision table in [references/DECISION_RULES.md][decision-rules].
   - If an overlap findings report is available, prefer reusing an existing skill or extracting a building block when the report shows a strong capability overlap.
   - **Completion criterion:** a primary shape is recommended with rationale.
5. **Present recommendation.**
   - Explain the primary recommendation, alternatives, and trade-offs.
   - If an overlap findings report informed the recommendation, summarize the key evidence (e.g., "three existing skills already implement `tool-discovery`, so extracting a building block is recommended").
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

## Existing options considered
- Local skills from `list-available-skills`.
- Registry results from `search-skills-registry` (if run).
- Overlap findings from `detect-skill-overlap` (if provided), including reuse / colocate / extract options.

## Recommendation
{skill | script | MCP server | context file | mode | reuse existing skill | extract building block}

## Rationale
...

## Alternatives considered
- ...

## Suggested next action
- ...
```

## Decision rules

For the full decision table and worked examples, see [references/DECISION_RULES.md][decision-rules]. At a high level:

| Shape | When to choose |
|---|---|
| **New skill** | Repeated, judgment-shaped task that can fire autonomously or by name. |
| **Existing skill** | The problem is already covered by a local or third-party skill. |
| **Script** | Narrow, deterministic task with a clear input/output transformation. |
| **MCP server** | The task needs external tools, real-time data, or sandboxed execution. |
| **Context file** | Reference, configuration, or shared conventions that skills consume. |
| **Mode** | Always-on guidance or a persistent persona that shapes behavior. |

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

`list-available-skills` is used for discovery during the alternatives step. It does not change the shape of the recommendation; it only surfaces existing options that might already cover the problem.

See [references/DEPENDENCIES.md][dependencies] for required tools and binaries.

## References

- [Decision rules][decision-rules]
- [Worked examples][worked-examples]
- `context-reports` skill — shared context-report conventions.
- `write-a-skill` — conductor for creating, reviewing, and updating skills.

[decision-rules]: references/DECISION_RULES.md
[dependencies]: references/DEPENDENCIES.md
[worked-examples]: references/EXAMPLES.md
