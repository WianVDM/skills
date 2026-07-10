---
name: debrief
description: "Debrief a ticket before implementation. Use when the user asks to 'understand a ticket', 'debrief a ticket', 'scope this ticket', or 'what does this ticket need'."
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [ticket, debrief, research, confidence, conductor]
depends:
  - checkpoint
  - research-ticket
  - map-ticket-relationships
  - explore-code
  - challenge-assumptions
  - scan-context
  - context-reports
  - worker-contract
  - detect-project-context
---

# debrief

## Purpose

Produce a structured, confidence-rated understanding of **one ticket** before implementation.

## Scope

### In scope

- Resolve a single ticket key from user input, branch, previous state, or explicit ask.
- Gather ticket data, relationships, codebase evidence, and related context reports.
- Form and challenge explicit assumptions.
- Calculate confidence and identify gaps.
- Write a structured debrief report and maintain resume state.
- Present a concise summary to the user.

### Out of scope

- **Handle multiple tickets in one invocation.** Debrief exactly one ticket per run.
- **Implement, test, or modify code.** This is investigation only.
- **Recommend the next skill.** `debrief` ends with a report, not a plan.
- **Decide execution order.** It produces understanding, not a task sequence.
- **Ask the user questions** except when a required input is missing or confidence is Red.

## Branches

| Branch | Trigger | Outcome |
|---|---|---|
| **new** | No existing state for this ticket, or the user explicitly asks for a fresh debrief. | Run the full 5-phase workflow. |
| **resume** | A `checkpoint` state file exists for this ticket and is fresh. | Resume from the last completed phase. |
| **manual** | The tracker is `manual` or credentials are missing. | Ask the user for ticket context and continue. |
| **blocked** | A required capability is missing. | Stop and report the blocker. |

## Workflow

Each phase ends by updating `checkpoint` state. The conductor always records the current focus and the last completed action.

### Phase 0 — Bootstrap and resume

**Completion criterion:** Project context is detected, config is loaded, the ticket key is resolved, tracker credentials are resolved, and `checkpoint` state is created or resumed.

Steps:

1. Detect project context (`detect-project-context`).
2. Load config (`load-skill-config`) with the defaults from `references/CONFIG_PATTERN.md`.
3. Detect the issue tracker (`detect-issue-tracker`) if `issue_tracker: auto`; otherwise validate the configured tracker.
4. Extract the ticket key (`extract-ticket-key`) from user input, branch, or previous state.
5. Get git state (`get-git-state`) if needed.
6. Resolve tracker credentials (`resolve-tracker-credentials`).
7. Create or resume checkpoint (`checkpoint`) at `{context_dir}/debrief/{key}/state.md`.
8. If any required capability is missing, report `blocked` and stop.

### Phase 1 — Gather evidence

**Completion criterion:** `research-ticket` has returned, `map-ticket-relationships` has returned, related context reports are discovered, and `baseline` has run or been skipped with a recorded reason.

Steps:

1. Research the ticket (`research-ticket`).
2. Map relationships (`map-ticket-relationships`).
3. Explore code (`explore-code`) only if the task type is `code`/`ui` or a code-related ambiguity exists.
4. Scan context (`scan-context`) for related baseline reports, handoffs, or prior debriefs.
5. Detect verifiable state (`detect-verifiable-state`).
6. Run `baseline` according to `baseline_mode`:
   - If `baseline_mode` is `skip`, record the skip reason and do not run `baseline`.
   - If `baseline_mode` is `required` and `detect-verifiable-state` returns `verifiable: false`, stop and ask the user for the observable state or the acceptance criteria that make the ticket verifiable. Record the user's response in `checkpoint`.
   - If `baseline_mode` is `required` or `optional` and `detect-verifiable-state` returns `verifiable: true`, run `baseline`. If `baseline` returns `needs_input`, surface the question to the user and record the response in `checkpoint`.
   - If `baseline_mode` is `optional` and `detect-verifiable-state` returns `verifiable: false`, record the skip reason and continue.
7. Update `checkpoint`.

### Phase 2 — Form and challenge assumptions

**Completion criterion:** Assumptions are formed, challenged, confidence is calculated, and any Red-confidence blockers are either resolved by the user or recorded as unresolved.

Steps:

1. Identify ambiguities from the gathered evidence.
2. Form explicit assumptions (`form-assumptions` subagent). The subagent returns a worker-contract result; the conductor extracts the `assumptions` object from the `## Findings` section.
3. Challenge assumptions (`challenge-assumptions`).
4. Calculate confidence (`calculate-confidence`).
5. If confidence is Red (below the threshold), produce a blocker report and ask the user to resolve the blockers. Record overrides in `checkpoint`.
6. Loop back to evidence gathering only if the user provides new information, up to `max_resolution_loops` times.
7. Update `checkpoint`.

### Phase 3 — Synthesize

**Completion criterion:** The debrief report is written to `{context_dir}/debrief/{key}-{slug}.md` and `checkpoint` marks the synthesize phase complete.

Steps:

1. Synthesize the final report (`synthesis-writer` subagent) from all evidence, assumptions, and confidence. The subagent returns a worker-contract result; the conductor extracts the written `report_path` from the `artifacts` frontmatter and the summary from the `## Summary` section.
2. Check whether `{context_dir}/debrief/{key}-{slug}.md` already exists. If it does, confirm with the user before overwriting and record the decision in `checkpoint`. If the user declines, append a suffix or choose a new slug and confirm again.
3. Write the report incrementally: update the report file after each phase so that context compaction does not lose progress.
4. Finalize the report at the canonical path.
5. Update `checkpoint`.

### Phase 4 — Present

**Completion criterion:** A concise summary is delivered to the user and the final `checkpoint` state is recorded.

Steps:

1. Present the ticket, confidence level, key assumptions, confidence gaps, and report path.
2. Record final state in `checkpoint`.

## State and report paths

```text
{context_dir}/
├── debrief/
│   ├── {key}-{slug}.md      # canonical debrief report
│   └── {key}/
│       └── state.md          # checkpoint state
```

## Dependencies

See `references/DEPENDENCIES.md` for the full dependency surface.

## Configuration

See `references/CONFIG_PATTERN.md` for the `debrief.yaml` schema and defaults.

## Subagents

- `subagents/form-assumptions.md` — turns ambiguities into explicit assumptions.
- `subagents/synthesis-writer.md` — writes the final debrief report from evidence and state.

## Lazy-loading gates

- `baseline` is only loaded when `detect-verifiable-state` returns `verifiable: true` and `baseline_mode != skip`.
- `explore-code` is only loaded when the task type is `code`/`ui` or a code-related ambiguity exists.
- `scan-context` is only loaded when the conductor wants to discover related reports.
- `map-ticket-relationships` is only loaded when the tracker provides relationship data or the user asks for it.

## Security

- No secrets are stored in skill files or config.
- Tracker tokens are referenced by env var name, not value.
- Confirm before overwriting an existing debrief report.
- Fail closed when a required capability is missing.
- Prefer read-only inspection in untrusted projects; ask before writing.

## Evaluation

- Trigger evals: `evals/evals.json`.
- Composition tests: verify the conductor invokes the correct building blocks in the correct order.
- Pressure tests: missing credentials, stale reports, Red-confidence loops, and manual tracker fallback.
