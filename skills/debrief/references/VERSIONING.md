# Versioning

## Current version

`debrief` is at version `3.0`.

This bump from `2.0` to `3.0` aligns the skill with the refactored `baseline` skill, reclassifies `debrief` as a conductor skill, and formalizes the dependency and context-report contracts.

---

## Report schema changes (v2 → v3)

The debrief report frontmatter (`.agents/context/debrief/{key}-{slug}.md`) has gained these fields:

- `generated_at` — ISO 8601 timestamp when the report was first created.
- `updated_at` — ISO 8601 timestamp of the last update (previously `debriefed_at`).
- `branch` — the current branch at generation time.
- `commit` — the current commit hash at generation time.
- `consumed_context` — list of related context reports read before or during the debrief.
- `artifacts_dir` — directory containing evidence, relative to `.agents/context/debrief/`.

The `version` field in the frontmatter is now `3`.

The state file (`.agents/context/debrief/{key}/state.md`) frontmatter version has also been bumped from `1` to `3`. No required fields were removed.

---

## State schema changes (v1 → v3)

- The state file frontmatter `version` is now `3`.
- No required fields were removed.
- No required fields were renamed.

Old state files are compatible because the main skill only requires the fields it reads and handles missing fields gracefully.

---

## Migration guidance

### Reading older reports

Consumers may read v1 and v2 reports, but they should treat them as potentially stale:

- v1 reports may lack `branch`, `commit`, `generated_at`, and `consumed_context`.
- v2 reports may lack `generated_at`, `consumed_context`, `branch`, and `commit`.

If a consumer needs those fields, it should either regenerate the report or read the state file and git state separately.

### Regenerating reports

If a report is older than the ticket's last update, or if the current branch/commit differs from the recorded values, the skill should regenerate the report rather than reuse it. See [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md) for freshness rules.

### State file compatibility

Old state files (`version: 1` or `version: 2`) can be read safely. The skill will update the version to `3` on the next write. No manual migration is required.

---

## Future version notes

When the schema changes again, update this file with:

- The new version number.
- A list of added, removed, or renamed fields.
- Migration guidance for consumers and existing reports.
- Any breaking changes that require manual intervention.
