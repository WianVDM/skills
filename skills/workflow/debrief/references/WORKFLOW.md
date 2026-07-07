# Workflow

This document is the detailed reference for the `debrief` skill's 7-phase workflow. The main [SKILL.md](../SKILL.md) uses a compressed overview; use this file when you need the full step-by-step process for implementation or troubleshooting.

The 7 phases are designed for parallel execution where possible. Independent subagents run concurrently up to `max_parallel_subagents` (default 3). The phase mapping is included after the process overview.

---

## 7-phase process

### Phase 0 — Bootstrap

1. Detect the project marker directory using `.agents`, `.pi`, `agents`, or a user-specified marker.
2. Load `{marker_dir}/config/shared.yaml` and `{marker_dir}/config/debrief.yaml`.
3. Detect available issue trackers (Jira, GitHub, Linear, manual).
4. Resolve the ticket key from user input, branch, or previous state; ask the user if needed.
5. Collect manual fallback context if no tracker is available.
6. Validate required capabilities (filesystem, tracker/user context, codebase access).
7. Persist resolved config and state with user confirmation.

### Phase 1 — Gather evidence (parallel)

Launch in parallel up to `max_parallel_subagents`:

- `ticket-researcher` — core ticket, comments, attachments, history, related tickets, development info.
- `code-explorer` — initial codebase sweep based on ticket summary and mentioned files.
- `related-context-scanner` — discover related artifacts in `{context_dir}/`.
- `duplicate-detector` — check for duplicate or already-implemented tickets.
- `task-type-classifier` — classify the ticket type (`code`, `ui`, `docs`, `process`, `unknown`).

### Phase 2 — Build context graph and identify ambiguities

1. Merge evidence from all sources into a context graph.
2. Compare ticket claims against codebase evidence.
3. Identify ambiguities: missing info, contradictions, multiple interpretations.
4. Form explicit assumptions for each ambiguity, with confidence and basis.
5. Update the debrief document skeleton with sections marked `pending`.

### Phase 3 — Resolve ambiguities (parallel)

For each ambiguity, choose an investigation path:

- **Code-related** → `code-explorer` (time-boxed).
- **Assumption stress-test** → `assumption-challenger` (searches for disproof).
- **Missing tracker context** → `ticket-researcher`.
- **User clarification needed** → surface to the user immediately.

Independent ambiguities are investigated in parallel. Maintain a visited set for related tickets to prevent circular references. Respect `max_related_depth` and `max_investigation_rounds`.

### Phase 4 — Baseline (conditional)

1. Decide if the ticket involves verifiable state using `detect-verifiable-state.py` or task type.
2. If relevant, invoke the `baseline` skill via `baseline-invoker`.
3. Handle `needs_input` and failure responses from baseline.
4. Record baseline status in state and report.

### Phase 5 — Synthesize and validate

1. Delegate to `synthesis-writer` to compile all evidence into the final report.
2. Update frontmatter with confidence, status, and confidence gap.
3. Delegate to `checkpoint-manager` to validate all phases are complete and consistent.

### Phase 6 — Present

1. Generate a concise chat summary for the user.
2. Save the final report to `{context_dir}/debrief/{key}-{slug}.md`.
3. Update the state file at `{context_dir}/debrief/{key}/state.md`.
4. If confidence < `confidence_threshold`, save a blocker report to `{context_dir}/debrief/{key}-blockers.md`.
5. Include tool suggestions if a helpful tool exists but is not configured.
6. Present the summary, confidence, assumptions, and escalations.

---

## Mapping to the seven phases

| Phase | Name | Output |
|-------|------|--------|
| 0 | Bootstrap | Project marker detected, config loaded, ticket key resolved |
| 1 | Gather evidence | Context graph populated, duplicate status known, task type classified |
| 2 | Build context graph | Ambiguities list populated, assumptions formed |
| 3 | Resolve ambiguities | Codebase evidence, assumptions updated, confidence recalculated |
| 4 | Baseline | Baseline status recorded |
| 5 | Synthesize and validate | Final debrief report complete and consistent |
| 6 | Present | Artifacts saved, user informed |

---

## Incremental output and checkpointing

The debrief document is written incrementally, not produced only at the end. This protects against context compaction and makes the current state inspectable at any time.

At the start, create a skeleton document with each section marked `<!-- STATUS: pending -->`. As each section is completed, replace the marker with `<!-- STATUS: completed -->` and fill the content. The state file tracks which phases are complete, which are in progress, and what the current focus is.

After every subagent returns, and after any context compaction:

1. Update the debrief document with the new findings.
2. Ask the `checkpoint-manager` to update the phase checklist and current focus.
3. Re-read the state file and debrief document before deciding the next action.

See [CHECKPOINTING.md](CHECKPOINTING.md) for phase definitions and self-validation prompts.

---

## Recontextualization after compaction

If the session context is compacted, the agent must not guess where it left off. Instead:

1. Read `{context_dir}/debrief/{key}/state.md`.
2. Read `{context_dir}/debrief/{key}-{slug}.md`.
3. Ask `checkpoint-manager` to summarize: completed phases, pending phases, current focus, and recommended next action.
4. Resume from the first pending phase.
5. Do not restart completed phases unless new information contradicts them.

---

## Context graph

The skill gathers evidence from multiple sources:

| Source | What to capture |
|--------|-----------------|
| Core ticket | Summary, description, acceptance criteria, status, priority |
| Related tickets | Parent, child, linked, duplicated, referenced |
| Development info | PRs, branches, commits |
| Codebase | Files mentioned, related patterns, similar features |
| User input | Clarifications, screenshots, notes |
| Baseline | UI evidence, reproduction results |

Record each source in state with a relevance score and what it contributed.

---

## Assumption handling

- Form explicit assumptions for every ambiguity.
- Rate each assumption's confidence and alignment.
- Challenge assumptions by searching for disproof, not confirmation.
- Escalate only assumptions with low confidence or direct contradictions.

See [ASSUMPTIONS.md](ASSUMPTIONS.md).

---

## Baseline integration

Baseline is recommended for most tickets because it provides ground-truth evidence of current state. However, if the ticket clearly does not involve a verifiable UI, API, or code state, or if baseline cannot proceed, consult the user before skipping it. Never silently skip a baseline because of an auth prompt, unreachable target, or missing tool.

See [BASELINE-INTEGRATION.md](BASELINE-INTEGRATION.md).

---

## Confidence levels

Rate overall debrief confidence honestly:

| Level | Range | Meaning |
|-------|-------|---------|
| **Red** | 0-59% | Too many unresolved ambiguities or contradictions. |
| **Yellow** | 60-84% | Some assumptions made, documented and reasonable. |
| **Green** | 85-100% | Clear understanding with confident resolutions. |

---

## Output location

Canonical outputs live under the detected context directory:

```text
{context_dir}/debrief/
├── {key}-{slug}.md              # final debrief report
├── {key}-blockers.md            # blocker report (if confidence < threshold)
└── {key}/
    └── state.md                 # resume/checkpoint state
```

---

## Hard stops

Stop and consult the user if:

- No ticket key can be resolved.
- No issue tracker or manual context is available.
- The ticket contradicts itself or related work.
- Baseline is required for this ticket but cannot proceed, and the user does not approve skipping.
- Confidence remains Red after exhausting available evidence.
