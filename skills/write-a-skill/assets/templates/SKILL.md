---
name: skill-name
description: Leading-word summary of what this skill does and when to trigger it. Include one trigger per branch.
license: Proprietary
metadata:
  author: your-name
  version: "1.0"
  scope: global | project-specific
invocation: model-invoked | user-invoked
disable-model-invocation: true  # only when user-invoked
---

# skill-name

## Purpose

State the single problem this skill owns and the specific outcome it produces.

## When to use

- A user asks for ...
- Another skill needs ...
- The user mentions trigger keywords: ...

## Out of scope

- This skill does not ...
- It does not ...

## Core workflow

1. **First step.** Describe the first action and its completion criterion.
2. **Next step.** Describe the next action and its completion criterion.
3. **Output.** Describe how the skill produces or updates its output.

For each step, include a **Completion criterion:** line that defines a checkable end state. If the skill has multiple branches with long workflows, disclose the detailed workflows in `references/BRANCH_WORKFLOWS.md` and keep only the branch summary and completion criterion here.

## References

- [Config pattern](references/CONFIG_PATTERN.md)
- [Context reports](references/CONTEXT_REPORTS.md)
- [Worker contract](references/WORKER_CONTRACT.md)
- [Branch workflows](references/BRANCH_WORKFLOWS.md) — if applicable
