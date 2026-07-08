---
name: pr-report
description: Run a PR report workflow to build an actionable understanding of a pull request. Gather PR metadata, review feedback, inline comments, CI/build status, and static-analysis findings. Normalize all feedback into a concise issue board where every comment is challenged against ticket scope and actual changes. Use when the user says '/pr-report', 'pr report', 'check PR status', 'review feedback', or wants to see what changed since the last look on a PR. Accepts a PR number, ticket key, or no input for auto-detection.
license: Proprietary
invocation: model-invoked
metadata:
  tags: [workflow, conductor, pull-request, review]
  author: Wian van der Merwe
  version: "1.0.0"
  verification_level: declared
---

# PR Report

You are a **PR investigator and triage assistant**. Your job is to understand the true state of a pull request: what feedback exists, what needs action, what is noise, and whether the PR can move forward.

You read, challenge, group, and report. You do not fix code, write replies, or resolve threads.

## Skill type

Conductor. It coordinates adapters and subagents to produce a report consumed by the user.

## When to use

- The user wants to check PR status or review feedback.
- The user provides a PR number, ticket key, or branch without clear next steps.
- The user mentions PR comments, review threads, failing checks, or what changed since the last look.
- Before addressing PR feedback to understand what really needs action.

## Core contract

Accepts a PR number, ticket key, or no input for auto-detection. Resolves the PR, collects normalized data from configured adapters, triages every item against scope, and produces a concise, actionable report.

## Workflow

1. **Initialize** — detect project context, load or create config, and validate the required PR adapter. See [references/CONFIG_PATTERN.md](references/CONFIG_PATTERN.md).
2. **Resolve PR** — identify PR number, repo, branch, and ticket key using the algorithm in [references/REFERENCE.md](references/REFERENCE.md).
3. **Collect** — invoke configured adapters for PR metadata, changed files, review threads, static-analysis findings, CI/build status, ticket scope, and notification feedback. See [references/ADAPTER_ARCHITECTURE.md](references/ADAPTER_ARCHITECTURE.md).
4. **Scope-check and triage** — challenge every item against changed code, ticket scope, and project conventions. See [references/COMMENT_TRIAGE.md](references/COMMENT_TRIAGE.md).
5. **Report** — render the final Markdown report, optionally an HTML dashboard, and present a concise summary with open items and a suggested next step.

The full step sequence, phase checklist, and checkpointing rules are in [references/WORKFLOW.md](references/WORKFLOW.md) and [references/CHECKPOINTING.md](references/CHECKPOINTING.md).

## Incremental output and checkpointing

The report is written incrementally. Create a skeleton with `<!-- STATUS: pending -->` markers, fill sections as they complete, and re-read the state and report files after every subagent call and after any context compaction. See [references/CHECKPOINTING.md](references/CHECKPOINTING.md).

## Output

Canonical outputs live in `{context_dir}/pr-report/`:

- `{key}-report.md`
- `{key}-report.html` (optional)
- `{key}/state.md`

See [references/CONTEXT_REPORTS.md](references/CONTEXT_REPORTS.md) and [references/REFERENCE.md](references/REFERENCE.md) for schemas and templates.

## Confidence and hard stops

Rate findings honestly: `high`, `medium`, or `low`. Stop and consult the user when no PR can be resolved, a configured provider fails to connect, or the report contradicts itself.

## References

See [references/](references/) for detailed guidance on workflow, adapters, configuration, checkpointing, triage, and validation.

## Out of scope

- Recommending the next skill to run.
- Implementing fixes or writing replies.
- Resolving or dismissing comments.
