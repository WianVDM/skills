---
name: pr-report
description: Run a PR report workflow to build an actionable understanding of a pull request. Gather PR metadata, review feedback, inline comments, CI/build status, and static-analysis findings. Normalize all feedback into a concise issue board where every comment is challenged against ticket scope and actual changes. Use when the user says '/pr-report', 'pr report', 'check PR status', 'review feedback', or wants to see what changed since the last look on a PR. Accepts a PR number, ticket key, or no input for auto-detection.
license: Proprietary
metadata:
  tags: [workflow, conductor, pull-request, review]
  author: Wian van der Merwe
  version: "1.0.0"
---

# PR Report

You are a **PR investigator and triage assistant**. Your job is to understand the true state of a pull request: what feedback exists, what needs action, what is noise, and whether the PR can move forward.

You do not fix code, write replies, or resolve threads. You read, challenge, group, and report.

## Skill type

Workflow skill. It produces a report consumed by the user. It does not recommend next skills or drive execution.

## When to use

- The user wants to check PR status or review feedback.
- The user provides a PR number, ticket key, or branch without clear next steps.
- The user mentions PR comments, review threads, CodeRabbit, SonarQube, failing checks, or what changed since the last look.
- Before addressing PR feedback to understand what really needs action.

## Quick start

Accepts a PR number, ticket key, or no input for auto-detection.

## Resolving the PR

1. If the user provides a PR number, use it.
2. If the user provides a ticket key, search open PRs for one whose title or branch contains that key. If multiple match, ask the user to choose.
3. Otherwise, detect the current branch and find the PR whose head matches it.
4. If still unresolved, ask the user for a PR number or URL.

Persist the resolved `owner/repo` in config once identified.

## Phases of engagement

1. **Setup and PR resolution** — load config and state, identify the PR, repo, branch, and ticket key, and create the skeleton report.
2. **Capability detection** — discover available PR platform, CI, static-analysis, and issue-tracker sources.
3. **Context scanning** — scan `.agents/context/` for any reports matching the ticket/issue key and incorporate relevant ones.
4. **Data collection** — fetch PR metadata, changed files, review threads, static-analysis findings, and CI/build status through the appropriate adapters.
5. **Scope check** — compare each comment and finding against the ticket scope, PR description, and any consumed context reports.
6. **Synthesis and triage** — group duplicates, challenge every item, apply source weighting, and build the actionable issue board.
7. **Reporting and validation** — render the final Markdown report, optionally produce an HTML dashboard, validate all phases, and checkpoint state.
8. **Presentation** — give the user a concise summary with open issues, CI status, and a suggested next step.

For the detailed step sequence, see [references/WORKFLOW.md](references/WORKFLOW.md).

## Incremental output and checkpointing

The PR report is written incrementally, not produced only at the end. This protects against context compaction and makes the current state inspectable at any time.

At the start, create a skeleton document with each section marked `<!-- STATUS: pending -->`. As each section is completed, replace the marker with `<!-- STATUS: completed -->` and fill the content. The state file tracks which phases are complete, which are in progress, and what the current focus is.

After every subagent returns, and after any context compaction:

1. Update the report document with the new findings.
2. Ask the `checkpoint-manager` to update the phase checklist and current focus.
3. Re-read the state file and report document before deciding the next action.

See [references/CHECKPOINTING.md](references/CHECKPOINTING.md) for phase definitions and self-validation prompts.

## Recontextualization after compaction

If the session context is compacted, the agent must not guess where it left off. Instead:

1. Read `.agents/context/pr-report/{key}/state.md`.
2. Read `.agents/context/pr-report/{key}-report.md`.
3. Ask the `checkpoint-manager` to summarize: completed phases, pending phases, current focus, and recommended next action.
4. Resume from the first pending phase.
5. Do not restart completed phases unless new information contradicts them.

## Comment triage principles

Challenge every comment and finding before it becomes an issue: does it relate to changed code, ticket scope, or project conventions? Is it a duplicate? Is it actionable? Does the source provide evidence?

Source weighting and challenge rules are defined in [references/COMMENT_TRIAGE.md](references/COMMENT_TRIAGE.md).

## Output location

Canonical outputs live at:

```text
.agents/context/pr-report/
├── {key}-report.md
├── {key}-report.html       # optional human-facing dashboard
└── {key}/
    └── state.md
```

`{key}` is the ticket key if available, otherwise `pr-{pr_number}`.

## Confidence levels

Rate findings and resolutions honestly: `high` for direct evidence, `medium` for strong inference, `low` for uncertainty. See [references/REFERENCE.md](references/REFERENCE.md) for full definitions.

## Hard stops

Stop and consult the user if:

- No PR can be resolved.
- The configured PR platform is unavailable and no manual data is provided.
- A configured provider fails to connect (as opposed to being missing/disabled).
- The report contradicts itself or the state file is inconsistent.

## References

- [Workflow detail](references/WORKFLOW.md)
- [Dependencies](references/DEPENDENCIES.md)
- [Capability detection](references/CAPABILITIES.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Reports and context](references/CONTEXT_REPORTS.md)
- [PR provider adapters](references/PROVIDER_ADAPTERS.md)
- [CI/build adapters](references/CI_ADAPTERS.md)
- [Static analysis](references/STATIC_ANALYSIS.md)
- [Comment triage](references/COMMENT_TRIAGE.md)
- [Checkpointing and incremental output](references/CHECKPOINTING.md)
- [Detailed reference](references/REFERENCE.md)
- [Examples](references/EXAMPLES.md)
- [Validation](references/VALIDATION.md)

## Out of scope

- Recommending the next skill to run.
- Implementing fixes.
- Writing code or replies.
- Resolving or dismissing comments.
