# Context Reports

The `debrief` skill produces and consumes reports in the project's shared context directory.

## Produced reports

Canonical reports live under the detected context directory:

```text
{context_dir}/debrief/{key}-{slug}.md
{context_dir}/debrief/{key}-blockers.md
{context_dir}/debrief/{key}/state.md
```

- `{key}-{slug}.md` — the canonical debrief report, written incrementally and finalized at the end.
- `{key}-blockers.md` — the blocker report, saved when confidence is below `confidence_threshold`.
- `{key}/state.md` — the resume anchor and working memory: phase checklist, context graph, ambiguities, baseline status, and next action.

The `{key}` placeholder is the resolved ticket key (e.g., `OC-4644`). The `{slug}` is a short, stable, human-readable suffix derived from the ticket summary (e.g., `auth-guard-race-condition`).

`{context_dir}` is detected at runtime via the project marker directory (`.agents`, `.pi`, `agents`, or user-specified). The skill does not assume a hardcoded `.agents/context/` path.

## Consumed reports

Before or during a debrief, the skill may read reports whose key matches the ticket or branch:

- `{context_dir}/baseline/{scope}-{branch}.md` — baseline evidence (optional). The `{scope}` may be the ticket key or a short feature slug.
- Any other `{context_dir}/{type}/{key}.md` or `{context_dir}/{type}/{key}*.md` whose filename or frontmatter contains the ticket key or branch name.

These reports are optional. The skill must handle their absence gracefully and must not fail if a specific report is missing. Discovered artifacts are consumed by schema and relationship, not by producer skill name.

## Report schema

Every debrief report must include this frontmatter:

```yaml
---
skill: debrief
version: 1.0.0
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-07-03T08:42:00Z
updated_at: 2026-07-03T08:42:00Z
summary: "Auth guard race condition during token refresh."
task_type: code
status: In Progress
priority: High
debrief_status: complete
debrief_confidence: Green (85%)
confidence_gap:
  - blocker: "Ticket does not specify expected behavior after refresh."
    why_it_blocks_full_confidence: "Could affect acceptance criteria."
    what_would_resolve_it: "PO confirmation or comment evidence."
    investigation_done: "Searched comments and related tickets; none found."
baseline_status: complete
consumed_context:
  - {context_dir}/baseline/OC-4644-SHB-362.md
artifacts_dir: OC-4644
assumptions:
  - assumption: "Token refresh happens in auth.guard.ts."
    basis: "Code in auth.guard.ts contains refresh logic; no interceptor found."
    confidence: 85
    alignment: Reasonable inference
    disproof_signals: "ADR mentioning interceptor, code in interceptor, tests referencing refresh.interceptor."
    impact_if_wrong: "Fix would move to interceptor."
    status: resolved
---
```

### Field definitions

| Field | Required | Description |
|---|---|---|
| `skill` | yes | Always `debrief`. |
| `version` | yes | The skill version that produced the report. |
| `ticket` | yes | The resolved ticket key. |
| `branch` | yes | The branch being worked on when the report was generated. |
| `commit` | yes | The current commit hash at generation time. |
| `generated_at` | yes | ISO 8601 timestamp when the report was first created. |
| `updated_at` | yes | ISO 8601 timestamp of the last update. |
| `summary` | no | One-sentence synthesis of the ticket. |
| `task_type` | yes | `code`, `ui`, `docs`, `process`, or `unknown`. |
| `status` | no | Ticket status from the tracker. |
| `priority` | no | Ticket priority from the tracker. |
| `debrief_status` | yes | `pending`, `in-progress`, or `complete`. |
| `debrief_confidence` | yes | Red/Yellow/Green with percentage. |
| `confidence_gap` | yes if < 100% | List of items blocking full confidence. |
| `baseline_status` | yes | `complete`, `skipped`, `failed`, `unavailable`, or `user_override`. |
| `consumed_context` | no | List of context reports read before or during the debrief. |
| `artifacts_dir` | no | Directory containing evidence, relative to `{context_dir}/debrief/`. |
| `assumptions` | yes | List of resolved/escalated assumptions with confidence and basis. |

### Incremental writing

The debrief document is created with all sections marked `pending` and updated as evidence arrives:

```markdown
# Debrief: {key} — [title pending]

<!-- STATUS: pending --> ## Overview
...
<!-- STATUS: completed --> ## Overview
...
```

As each section completes, replace `pending` with `completed` and add the content below the marker.

## Blocker report schema

Saved when `debrief_confidence` is below `confidence_threshold`:

```yaml
---
skill: debrief
type: blocker-report
version: 1.0.0
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-07-03T08:42:00Z
updated_at: 2026-07-03T08:42:00Z
summary: "Ticket is too vague to proceed with confidence."
---
```

Body sections:
- What is known
- What was investigated
- What is missing
- Why the risk is too high
- What the user needs to clarify

## State file schema

The state file at `{context_dir}/debrief/{key}/state.md` uses this frontmatter:

```yaml
---
skill: debrief
version: 1.0.0
ticket: OC-4644
updated_at: 2026-07-03T08:42:00Z
---
```

Body sections:

```markdown
# Debrief State: OC-4644

## Phase Checklist
- [x] Phase 0: Bootstrap
- [x] Phase 1: Gather evidence
- [x] Phase 2: Build context graph and identify ambiguities
- [x] Phase 3: Resolve ambiguities
- [x] Phase 4: Baseline
- [x] Phase 5: Synthesize and validate
- [x] Phase 6: Present

## Current Focus
Completed.

## Last Completed Action
Final debrief report validated and saved.

## Session History
...

## Context Graph
...

## Ambiguities
...

## Codebase Explored
...

## Baseline Status
...

## Ticket Context Cached
...

## Visited Related Tickets
| Ticket | Depth | Visited At |
|---|---|---|
| OC-1234 | 1 | 2026-07-03T08:00:00Z |

## Next Action
None — debrief complete.
```

### Session history pruning

When the `## Session History` table exceeds 20 rows, archive the oldest rows to `{context_dir}/debrief/{key}/state-history.md` and keep only the most recent iterations in the active state file.

See [CHECKPOINTING.md](CHECKPOINTING.md) for the full state file structure and resume rules.

## Report freshness

A debrief report is stale when any of the following are true:

- The current branch or commit differs from the recorded `branch` or `commit`.
- The ticket's `updated_at` (from the tracker) is newer than the report's `generated_at`.
- The report's `debrief_status` is not `complete` and the session was interrupted.
- A discovered artifact is older than `artifact_freshness_hours` (still consumed with caveats).

When reusing an existing report, the skill should verify freshness and either regenerate or note the staleness explicitly.

## Cross-skill consumption

Other skills that read debrief reports should:

1. Read the Markdown report at `{context_dir}/debrief/{key}-{slug}.md`.
2. Trust `ticket`, `branch`, `commit`, `generated_at`, and `updated_at` as the snapshot context.
3. Treat `consumed_context` as a hint for upstream context, not a hard dependency.
4. Check `version` if the report format matters to the consumer. See [VERSIONING.md](VERSIONING.md) for schema changes.
5. Treat `debrief_confidence` and `baseline_status` as advisory inputs, not blockers.
6. Treat `assumptions` and `confidence_gap` as the skill's honest assessment of uncertainty.
