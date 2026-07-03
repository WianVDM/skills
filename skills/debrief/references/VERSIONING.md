# Versioning

## Current version

`debrief` is at version `4.0`.

This bump from `3.0` to `4.0` makes `debrief` a global, pluggable conductor / skill base. It adds project-layout detection, a parallel 7-phase pipeline, task-type classification, duplicate detection, generic artifact discovery, structured assumption/confidence-gap schemas, and a blocker report.

---

## Report schema changes (v3 → v4)

The debrief report frontmatter (`{context_dir}/debrief/{key}-{slug}.md`) has gained these fields:

- `task_type` — `code`, `ui`, `docs`, `process`, or `unknown`.
- `confidence_gap` — list of items blocking 100% confidence.
- `assumptions` — structured list of resolved/escalated assumptions.
- `debrief_status` — `pending`, `in-progress`, or `complete`.

The `version` field in the frontmatter is now `4.0`.

The blocker report (`{context_dir}/debrief/{key}-blockers.md`) is a new artifact type.

The state file (`{context_dir}/debrief/{key}/state.md`) frontmatter `version` is now `4.0`.

Report paths are now relative to the detected project marker directory (`{context_dir}`), not a hardcoded `.agents/context/`.

---

## Config schema changes (v3 → v4)

`{marker_dir}/config/debrief.yaml` has gained these keys:

- `confidence_threshold` — default 85.
- `max_parallel_subagents` — default 3.
- `max_related_depth` — default 3.
- `max_investigation_rounds` — default 5.
- `artifact_freshness_hours` — default 24.
- `monorepo_workspace` — `auto`, package name, or null.
- `trackers` — multi-tracker configuration block.

Existing v3 configs are merged with v4 defaults. Missing keys are populated on first write and the user is notified.

---

## Migration guidance

### Reading older reports

Consumers may read v3 reports, but they should treat them as potentially missing new fields:

- v3 reports may lack `task_type`, `confidence_gap`, and `assumptions`.
- v3 report paths assume `.agents/context/`; v4 consumers should detect the project marker directory.

If a consumer needs the new fields, it should regenerate the report.

### Regenerating reports

If a report is older than the ticket's last update, if the current branch/commit differs from the recorded values, or if the report lacks v4 fields, the skill should regenerate the report rather than reuse it. See [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md) for freshness rules.

### State file compatibility

Old state files (`version: 3`) can be read safely. The skill will update the version to `4.0` on the next write. No manual migration is required.

### Config compatibility

Old v3 config files are merged with v4 defaults. Missing keys are populated with defaults. Invalid values are clamped to defaults and reported to the user.

---

## Historical schema notes

### v2 → v3

The debrief report frontmatter gained:

- `generated_at` — ISO 8601 timestamp when the report was first created.
- `updated_at` — ISO 8601 timestamp of the last update (previously `debriefed_at`).
- `branch` — the current branch at generation time.
- `commit` — the current commit hash at generation time.
- `consumed_context` — list of related context reports read before or during the debrief.
- `artifacts_dir` — directory containing evidence, relative to `{context_dir}/debrief/`.

The state file frontmatter `version` was bumped to `3`.

---

## Future version notes

When the schema changes again, update this file with:

- The new version number.
- A list of added, removed, or renamed fields.
- Migration guidance for consumers and existing reports.
- Any breaking changes that require manual intervention.
