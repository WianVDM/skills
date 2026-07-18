# Checkpointing and Incremental Output

`pr-report` is a long-running workflow. Context compaction is a real risk. The skill counters this by writing the report incrementally and delegating state management to the [`checkpoint`](../../../../blocks/project/checkpoint/SKILL.md) block.

## Core principle

> The report document and state file are the source of truth. The agent's memory is secondary. After every worker call and after any context compaction, re-read these files and resume from the first pending phase.

## State management

The state file at `{context_dir}/pr-report/{key}/state.md` is owned and maintained by the `checkpoint` block, which provides the schema and the `create`, `update`, `resume`, and `validate` operations. `pr-report` supplies:

- **Phases** (caller-defined strings): `resolve`, `prior-context`, `discover`, `collect`, `scope-check`, `triage`, `report`.
- **Owner frontmatter**: `pr_number`, `repo`, `branch`, `base`, `report_status`, `generated_at`, `commit_hash`.
- **Owner sections**: PR Info, Detected Tools, Reviews Tracked, Comment History, Static Analysis Findings, CI / Build Status, Triage Decisions, Scope Flags, Files Changed.

Invoke `checkpoint/update` after every worker returns: mark the completed phase, update Current Focus and Last Completed Action, and record the next pending phase. Invoke `checkpoint/resume` after context compaction and do not proceed until the state and report files have been re-read.

## Skeleton report document

At the start of the discover phase, create the report document with all sections marked pending:

```markdown
---
skill: pr-report
version: 1
key: OC-1234
pr_number: 1234
repo: owner/repo
branch: feature/OC-1234-something
base: origin/development
report_status: in-progress
generated_at: 2026-06-26T08:00:00Z
updated_at: 2026-06-26T08:00:00Z
---

# PR Report: [title pending] — Iteration {N}

<!-- STATUS: pending --> ## PR Summary
<!-- STATUS: pending --> ## Changed Files
<!-- STATUS: pending --> ## CI / Build Status
<!-- STATUS: pending --> ## Static Analysis Findings
<!-- STATUS: pending --> ## Issues Requiring Action
<!-- STATUS: pending --> ## Resolved Since Last Check
<!-- STATUS: pending --> ## Threads with Unclear Status
<!-- STATUS: pending --> ## Addressed by Us — Pending Resolve
<!-- STATUS: pending --> ## Rebuttals Requiring Response
<!-- STATUS: pending --> ## Reviewer Status
<!-- STATUS: pending --> ## Scope Flags
<!-- STATUS: pending --> ## Dismissed / No Action Needed
<!-- STATUS: pending --> ## Data Sources
<!-- STATUS: pending --> ## Task List
```

As sections are completed, replace `pending` with `completed` and fill the content. Mark a phase complete only after its output has been written to the report document.

## State validation and recovery

The conductor must handle corrupted or stale state gracefully:

- If the state file version does not match the current schema, archive it and start fresh.
- If the commit hash in state differs from the current PR head, archive the old state and start fresh (this is a new iteration, not a resume).
- If the state file cannot be parsed, archive it and start fresh.
- Always report to the user when state is reset or archived.

Archive path:

```text
{context_dir}/pr-report/archive/{key}-state-{old-version}-{timestamp}.md
```

## Self-validation prompts

Before moving from one phase to the next, answer:

1. Is the current phase complete?
2. Does the new information contradict anything already recorded?
3. What is the next phase, and what is its goal?
4. Is the current focus still correct?

## Resume rules

1. Invoke `checkpoint/resume` on `{context_dir}/pr-report/{key}/state.md`.
2. Re-read `{context_dir}/pr-report/{key}-report.md`.
3. Resume from the first pending phase in the Phase Checklist.
4. Do not restart completed phases unless new evidence contradicts them.
5. Update Current Focus before doing any work.

## Focus guardrails

If the agent finds itself doing work that does not serve the current Current Focus:

1. Stop.
2. Re-read the state file and report document.
3. Invoke `checkpoint/resume` if unsure.
4. Resume from the documented focus.

## Finalization

When all phases are complete:

1. Update `report_status` to `complete`.
2. Remove any remaining `pending` markers.
3. Invoke `checkpoint/validate` to verify completeness and consistency.
4. Present findings to the user.
