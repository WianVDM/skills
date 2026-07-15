---
name: scope-checker
description: Challenge a list of findings against a scope (ticket acceptance criteria, changed files, PR intent, or project conventions) and classify each one as in-scope, out-of-scope, or ambiguous. Use when a conductor needs to triage findings by whether they belong to the current work item.
version: 1.0.0
invocation: model-invoked
depends:
  - worker-contract
---

# scope-checker

## Purpose

Provide a reusable scope gate for conductors. Given a scope envelope and a list of findings, classify each finding as relevant to the scope, outside the scope, or ambiguous.

## Skill type

Building block. It classifies findings but does not change project state, dismiss findings, or make final decisions.

## When to use

A conductor needs to triage findings (PR comments, static-analysis issues, CI failures, or manual observations) against a defined scope. Use `scope-checker` when:

- A PR review needs to flag comments that drift outside the ticket scope.
- A static-analysis finding may apply to unchanged code.
- A CI failure or test failure may be unrelated to the current work item.
- The scope source is a ticket, PR, branch, or manual description.

## In scope

- Read a scope envelope (ticket acceptance criteria, PR title/body, changed files, or manual description).
- Read a list of findings with source, severity, location, and message.
- Compare each finding against the scope.
- Classify each finding as `in-scope`, `out-of-scope`, or `ambiguous`.
- Provide a reason for each classification.
- Return a summary count.

## Out of scope

- Dismissing or resolving findings.
- Changing project state or files.
- Making final decisions about what to fix.
- Asking the user directly. The conductor owns user interaction.

## Core contract

Accept a scope envelope and a findings list. Return each finding with a classification and reason, plus a summary.

The block is implemented as a subagent that follows the `worker-contract` return contract.

## Input

The parent skill passes the following in the subagent prompt:

- `scope`: object describing the scope.
- `findings`: array of findings to classify.
- `project_conventions`: optional list of convention references to consider.

See [references/INTERFACE.md](references/INTERFACE.md) for the full schema.

## Output

The subagent returns the standard `worker-contract` format with a `Findings` section that contains:

- `classified`: array of findings with classification and reason.
- `summary`: counts of `in-scope`, `out-of-scope`, and `ambiguous`.

See [references/INTERFACE.md](references/INTERFACE.md) for the full schema.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Interface](references/INTERFACE.md)
- [Dependencies](references/DEPENDENCIES.md)
- [Subagent](subagents/scope-checker.md)
- [worker-contract](../worker-contract/SKILL.md)
