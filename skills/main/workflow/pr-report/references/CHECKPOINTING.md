# Checkpointing and Incremental Output

`pr-report` is a long-running workflow. Context compaction is a real risk. The skill counters this by writing the report incrementally and using the state file as a persistent resume anchor.

## Core principle

> The report document and state file are the source of truth. The agent's memory is secondary. After every subagent call and after any context compaction, re-read these files and resume from the first pending phase.

## Phases

| Phase | Name | Output |
|-------|------|--------|
| 1 | Resolve PR and load context | PR number/repo/branch identified, config loaded |
| 2 | Create skeleton and discover tools | Report skeleton exists; `## Detected Tools` lists preferred tools |
| 3 | Collect data | PR metadata, reviews, threads, CI, static analysis, issue tracker scope |
| 4 | Scope check | Report section: Scope Flags |
| 5 | Triage and synthesize issues | Report sections: Issues Requiring Action, Resolved Since Last Check, etc. |
| 6 | Render final report | All sections marked complete, frontmatter updated, optional HTML generated |

Each phase is marked complete in the state file only after its output has been written to the report document.

## Skeleton report document

At the start of Phase 2, create the report document with all sections marked pending:

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

As sections are completed, replace `pending` with `completed` and fill the content.

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

## Checkpoint manager usage

Call `checkpoint-manager` after every subagent returns and after context compaction.

After a subagent returns:

- Read the current state file and report document.
- Mark the just-completed phase as complete if its sections are written.
- Update `Current Focus` and `Last Completed Action`.
- Identify the next pending phase.
- Return a concise status summary.

After context compaction:

- Read state and report.
- Report completed phases, pending phases, current focus, and recommended next action.
- Do not proceed until the main agent has re-read the files.

## Resume rules

1. Read `{context_dir}/pr-report/{key}/state.md`.
2. Read `{context_dir}/pr-report/{key}-report.md`.
3. Call `checkpoint-manager` for a status summary.
4. Resume from the first unchecked phase in `## Phase Checklist`.
5. Do not restart completed phases unless new evidence contradicts them.
6. Update `Current Focus` before doing any work.

## Focus guardrails

If the agent finds itself doing work that does not serve the current `## Current Focus`:

1. Stop.
2. Re-read the state file and report document.
3. Call `checkpoint-manager` if unsure.
4. Resume from the documented focus.

## Finalization

When all phases are complete:

1. Update `report_status` to `complete`.
2. Remove any remaining `pending` markers.
3. Ask `checkpoint-manager` to verify completeness and consistency.
4. Present findings to the user.
