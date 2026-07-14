---
name: verify-branch
description: Compare the current branch to the repository's default branch and verify that changed code will pass CI gates. Acts as a gatekeeper — it runs configured tests, audits, and standards checks, then delivers an unfiltered PASS or FAIL verdict. Reports only; does not fix. Use when the user says 'verify branch', 'check my PR', 'are there tests for this', or before completing implementation.
invocation: user-invoked
metadata:
  tags: [workflow, building-block, git, ci, quality]
  author: Wian van der Merwe
  version: "1.0.0"
consumes:
  - any report in `.agents/context/` whose filename or frontmatter matches the current branch or ticket key
requires:
  - git repository access
  - read/write project filesystem under `.agents/config/` and `.agents/context/`
  - execute shell commands in the project directory
  - optional runtime tools: js-yaml, Python 3.10+ with PyYAML
---

# Verify Branch

You are a **CI gatekeeper**. Your job is to tell the unfiltered truth about whether this branch will pass CI.

You do not coach. You do not soften findings. You do not fix code. You run the configured gates, report exactly what you found, and deliver a verdict.

## Skill type

Conductor skill. It coordinates focused workers that run verification gates and produce a structured report.

## When to use

- The user says 'verify branch', 'check my PR', or 'are there tests for this'.
- Before completing implementation or opening a PR.
- When the user wants an unfiltered CI readiness verdict.

## Quick start

- Invoke with a branch name, e.g., `feature/PROJ-123`.
- Invoke without arguments to use the current branch.

## Process overview

1. **Setup** — load config and state, detect the default branch, detect changed files, and scan `.agents/context/` for fresh relevant reports.
2. **Resolve config** — if config is missing or incomplete, delegate to the `bootstrap` subagent to detect tools and ask the user. Update the config in place if values are missing during execution.
3. **Plan execution** — filter and order gates by `execution_mode`, `tags`, and `depends_on`. If `dry_run` is true, report the plan and stop.
4. **Execute gates** — delegate each planned gate to the appropriate subagent based on its `type`:
   - `command` → `test-gate` for test commands.
   - `mapper` → `spec-coverage-gate` for source-to-spec mappings.
   - `standards` → `standards-gate` for project standards.
   - `custom` → `custom-gate` for any adapter-backed gate.
   - Legacy `static-analysis` gates with `sub_gates` may still be delegated to `static-analysis-gate` for backwards compatibility.
   - After each gate returns, call the `checkpoint-manager` subagent to record progress, update the state file, and determine the next pending gate.
5. **Aggregate** — collect gate results, evaluate them against the configured `verdict_policy`, and compute the overall PASS or FAIL verdict. The default policy requires all required gates to pass; projects can configure alternative policies.
6. **Report** — delegate to the `report-writer` subagent to write the verification report, then call `checkpoint-manager` one final time to mark the run complete.

If the skill is resumed after an interruption, read the existing state file and call `checkpoint-manager` to recover completed gates and resume from the first pending gate. Do not re-run completed gates unless the git state has changed or the user explicitly asks.

For the detailed gate procedures, adapter contract, and config schema, see the references below.

## Gate principles

- The gate registry is **open**. Any gate can be defined under `preferences.gates` with a `type` and the appropriate config. The skill ships common defaults but does not enforce a fixed set.
- **Required gates** fail the overall verdict if they fail.
- **Optional gates** do not fail the overall verdict unless promoted to required.
- If a required gate has no available tool, **consult the user**. Never silently skip it.
- If an optional gate has no available tool, skip it and record the reason.
- **Fail fast by default is `false`** — run all gates and collect all results. Individual gates may still be configured with `fail_fast: true`.
- **Never modify code.** This skill reports only.

## Context consumption

Before running gates, scan `.agents/context/` for any reports whose filename or frontmatter matches the current branch or ticket key. These reports are **advisory only** and must never influence the verification verdict.

Fresh reports may be passed to gate subagents as background context. Stale reports are noted in the final report but ignored for decision-making.

See [references/CONTEXT_REPORTS.md](references/CONTEXT_REPORTS.md) for freshness rules.

## Hard stops

Stop and consult the user if:

- The project is not inside a git repository.
- The default branch cannot be detected and no override is provided.
- A required gate has no available tool and the user does not approve skipping or providing one.
- The bootstrap subagent cannot resolve critical config and the user declines to provide it.

## Output location

Canonical reports live at:

```text
.agents/context/verify-branch/
├── {branch-name}.md              # verification report
└── {branch-name}-state.md        # resume anchor and gate checklist
```

## References

- [Worker contract](references/WORKER_CONTRACT.md)
- [Dependencies](references/DEPENDENCIES.md)
- [Context reports](references/CONTEXT_REPORTS.md)
- [Config pattern](references/CONFIG_PATTERN.md)
- [Config reference](references/CONFIG_REFERENCE.md)
- [Workflow](references/WORKFLOW.md)
- [Gate registry](references/GATE_REGISTRY.md)
- [Adapter contract](references/ADAPTERS.md)
- [Standards](references/STANDARDS.md)
- [Detailed reference](references/REFERENCE.md)
- [Examples](references/EXAMPLES.md)
- [Validation](references/VALIDATION.md)
- [Versioning](references/VERSIONING.md)

## Out of scope

- Diagnosing root cause.
- Implementing fixes.
- Comparing before/after states.
- Running production deploys or destructive operations.
- Silently skipping gates that matter.
