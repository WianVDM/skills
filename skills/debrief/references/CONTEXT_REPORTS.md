# Context Reports

The `debrief` skill produces and consumes reports in the shared context directory.

---

## Produced reports

Canonical reports live at:

```text
{project-root}/.agents/context/debrief/{key}-{slug}.md
{project-root}/.agents/context/debrief/{key}/state.md
```

- `{key}-{slug}.md` — the canonical debrief report, written incrementally and finalized at the end.
- `{key}/state.md` — the resume anchor and working memory: phase checklist, context graph, ambiguities, baseline status, and next action.

The `{key}` placeholder is the resolved ticket key (e.g., `OC-4644`). The `{slug}` is a short, stable, human-readable suffix derived from the ticket summary (e.g., `auth-guard-race-condition`).

---

## Consumed reports

Before or during a debrief, the skill may read reports whose key matches the ticket or branch:

- `.agents/context/baseline/{scope}-{branch}.md` — baseline evidence (optional). The `{scope}` may be the ticket key or a short feature slug.
- Any other `.agents/context/{type}/{key}.md` or `.agents/context/{type}/{key}*.md` whose filename or frontmatter contains the ticket key or branch name.

These reports are optional. The skill must handle their absence gracefully and must not fail if a specific report is missing.

---

## Report schema

Every debrief report must include this frontmatter:

```yaml
---
skill: debrief
version: 3
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-06-30T08:42:00Z
updated_at: 2026-06-30T08:42:00Z
summary: "Auth guard race condition during token refresh."
debrief_confidence: Green (90%)
baseline_status: complete
consumed_context:
  - .agents/context/baseline/OC-4644-SHB-362.md
artifacts_dir: OC-4644
---
```

### Field definitions

| Field | Required | Description |
|-------|----------|-------------|
| `skill` | yes | Always `debrief`. |
| `version` | yes | The skill version that produced the report. |
| `ticket` | yes | The resolved ticket key. |
| `branch` | yes | The branch being worked on when the report was generated. |
| `commit` | yes | The current commit hash at generation time. |
| `generated_at` | yes | ISO 8601 timestamp when the report was first created. |
| `updated_at` | yes | ISO 8601 timestamp of the last update. |
| `summary` | no | One-sentence synthesis of the ticket. |
| `debrief_confidence` | yes | Red/Yellow/Green with percentage. |
| `baseline_status` | yes | `pending`, `in-progress`, `complete`, `failed`, `skipped`, or `unavailable`. |
| `consumed_context` | no | List of context reports read before or during the debrief. |
| `artifacts_dir` | no | Directory containing evidence, relative to `.agents/context/debrief/`. |

### State file schema

The state file at `.agents/context/debrief/{key}/state.md` uses this frontmatter:

```yaml
---
skill: debrief
version: 3
ticket: OC-4644
updated_at: 2026-06-30T08:42:00Z
---
```

See [CHECKPOINTING.md](CHECKPOINTING.md) for the full state file structure.

---

## Report freshness

A debrief report is stale when any of the following are true:

- The current branch or commit differs from the recorded `branch` or `commit`.
- The ticket's `updated_at` (from the tracker) is newer than the report's `generated_at`.
- The report's `debrief_status` is not `complete` and the session was interrupted.

When reusing an existing report, the skill should verify freshness and either regenerate or note the staleness explicitly.

---

## Cross-skill consumption

Other skills that read debrief reports should:

1. Read the Markdown report at `.agents/context/debrief/{key}-{slug}.md`.
2. Trust the `ticket`, `branch`, and `commit` fields as the authoritative snapshot context.
3. Treat the `consumed_context` list as a hint for upstream context, not as a hard dependency.
4. Check `version` if the report format matters to the consumer. See [VERSIONING.md](VERSIONING.md) for schema changes.
5. Treat `debrief_confidence` and `baseline_status` as advisory inputs, not blockers.
