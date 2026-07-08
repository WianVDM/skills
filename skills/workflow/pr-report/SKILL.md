---
name: pr-report
description: Build an actionable understanding of a pull request. Gather PR metadata, review feedback, inline comments, CI/build status, and static-analysis findings by selecting the best available tool for each capability. Normalize all feedback into a concise issue board where every comment is challenged against ticket scope and actual changes. Use when the user says '/pr-report', 'pr report', 'check PR status', 'review feedback', or wants to see what changed since the last look on a PR. Accepts a PR number, ticket key, or no input for auto-detection.
license: Proprietary
invocation: model-invoked
metadata:
  tags: [workflow, conductor, pull-request, review]
  author: Wian van der Merwe
  version: "1.0.1"
depends:
  - detect-project-context
  - context-reports
  - worker-contract
  - token-resolver
  - pr-adapter-contract
  - manual-pr-adapter
  - github-pr-adapter
  - github-actions-adapter
  - sonarcloud-adapter
  - jira-adapter
  - debrief
  - baseline
---

# PR Report

## Purpose

Build a single, trustworthy, actionable understanding of a pull request by selecting the best available tool for every capability the report needs.

## Skill type

Conductor. It coordinates tools, adapters, and subagents to produce a report consumed by the user.

## When to use

- The user wants to check PR status or review feedback.
- The user provides a PR number, ticket key, or branch without clear next steps.
- The user mentions PR comments, review threads, failing checks, or what changed since the last look.
- Before addressing PR feedback to understand what really needs action.

## Core contract

Accepts a PR number, ticket key, or no input for auto-detection. Resolves the PR, selects the best available tool for each capability, collects normalized data from those tools, triages every item against scope, and produces a concise, actionable report.

The skill does not treat its own adapters as the only source of truth for any capability. Adapters, MCP tools, native binaries, direct APIs, and manual fallback are all candidates for each capability.

## Workflow

1. **Initialize** — detect project context, load or create config, and validate that at least one PR source tool is available. **Completion:** `{config_dir}/pr-report.yaml` exists, the PR capability has a selected tool, and its token resolves without error.
2. **Resolve PR** — identify PR number, repo, branch, and ticket key. **Completion:** `pr_number`, `repo`, `branch`, and `key` are recorded in `{context_dir}/pr-report/{key}/state.md`.
3. **Discover tools** — for each load-bearing capability (PR source, top-level reviews, inline threads, changed files, CI/build, static analysis, issue tracker, notification feedback), detect available tools: configured adapters, MCP tools/servers, native binaries, direct APIs, and manual fallback. Record the ranked list and the preferred tool in state. **Completion:** For every capability, at least one tool is detected and the preferred tool is identified; the ranking is recorded in state.
4. **Collect** — invoke the preferred tool for each capability. If the preferred tool returns partial or no data and a better-ranked tool is available, fall back to the next-best tool before accepting degradation. **Completion:** Every capability has returned data from the best available tool, or the user has explicitly accepted a degraded source.
5. **Scope-check and triage** — challenge every item against changed code, ticket scope, and project conventions. **Completion:** Every item is classified as actionable, resolved, outdated, or no-action-needed; the issue board is recorded in the report.
6. **Report** — render the final Markdown report, optionally an HTML dashboard, and present a concise summary with open items and a suggested next step. **Completion:** All report sections are marked `<!-- STATUS: completed -->`, `report_status` is `complete`, and the chat summary is delivered.

The full step sequence, phase checklist, and resume rules are in [references/WORKFLOW.md](references/WORKFLOW.md) and [references/CHECKPOINTING.md](references/CHECKPOINTING.md). The capability-to-tool mapping is in [references/TOOL_SELECTION.md](references/TOOL_SELECTION.md).

## Incremental output and checkpointing

The report is written incrementally. Create a skeleton with `<!-- STATUS: pending -->` markers, fill sections as they complete, and re-read the state and report files after every subagent call and after any context compaction. See [references/CHECKPOINTING.md](references/CHECKPOINTING.md).

## Output

Canonical outputs live in `{context_dir}/pr-report/`:

- `{key}-report.md`
- `{key}-report.html` (optional)
- `{key}/state.md`

See [references/CONTEXT_REPORTS.md](references/CONTEXT_REPORTS.md) and [references/REFERENCE.md](references/REFERENCE.md) for schemas and templates.

## Confidence and hard stops

Assign a confidence to every resolution and synthesized issue: `high` only when direct evidence exists; `medium` for strong inference; `low` when uncertainty remains. Surface `low` confidence items explicitly in the chat summary.

Stop and consult the user when:

- No PR can be resolved after the algorithm in `references/REFERENCE.md`.
- A configured provider fails to connect (as opposed to being missing or disabled).
- The report contradicts itself or the state file is inconsistent.
- A better tool is available for a capability but the skill is about to accept a degraded source. Ask the user whether to use the better tool, accept the degraded source, or skip the capability.

## References

See [references/](references/) for detailed guidance on workflow, tool selection, adapters, configuration, checkpointing, triage, and validation.

## Out of scope

- Recommending the next skill to run.
- Implementing fixes or writing replies.
- Resolving or dismissing comments.
- Treating the skill's built-in adapters as the only source of truth for any capability.
