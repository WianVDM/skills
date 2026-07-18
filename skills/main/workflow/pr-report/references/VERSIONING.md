# Versioning

`pr-report` produces reports and state files consumed by other skills and by the user. This document defines how report/state schema changes are handled. Skill versioning is being refactored across the repo and is intentionally not declared in frontmatter for now.

## Version concepts

| Concept | Location | Changes when |
|---|---|---|
| **Report / state schema version** | `version` field in report and state frontmatter | Sections, frontmatter fields, or delta classifications are added, removed, or renamed. |

## Current versions

- Report/state schema version: `1`

## Breaking changes

Breaking: removing or renaming a report section or field; changing a field's meaning; changing normalization-contract usage or a worker's return format in a way that breaks consumers. Non-breaking: adding optional sections or fields, adding providers, wording clarifications.

## Migration path

When loading an existing state or report file:

1. Read its `version` field. If current, use it directly.
2. If older but backward compatible, read what is present and treat missing fields as default.
3. If older and incompatible, archive the file and start fresh. Append-only history tables are migrated when possible rather than discarded.

Stale artifacts are moved to `{context_dir}/pr-report/archive/{key}-{artifact}-{old-version}.md`; the new artifact records the archive path in `archived_artifacts` or state notes.

## Config schema migration

When the config schema changes, load the existing config, map known old keys automatically, ask about ambiguous ones, persist the migrated config, and append a migration note.

### Old adapter-shaped config mapping

| Old key | New key | Mapping rule |
|---|---|---|
| `adapters.pr.source: github-pr-adapter` | `pr-report.tools.pr.provider: github` | Map adapter name to provider name. |
| `adapters.pr.source: manual-pr-adapter` | `pr-report.tools.pr.provider: manual` | Map to manual provider. |
| `adapters.pr.source: auto` | `pr-report.tools.pr.provider: auto` | No change. |
| `adapters.ci.source: github-actions-adapter` | `pr-report.tools.ci.provider: github-actions` | Map adapter name to provider name. |
| `adapters.static_analysis.source: sonarcloud-adapter` | `pr-report.tools.static_analysis.provider: sonarcloud` | Map adapter name to provider name. |
| `adapters.issue_tracker.source: jira-adapter` | `pr-report.tools.issue_tracker.provider: jira` | Map adapter name to provider name. |
| `tooling.preference` | `pr-report.tooling.preference` | No change. |
| `tooling.degraded_mode` | `pr-report.tooling.degraded_mode` | No change. |
| `bots` | `pr-report.bots` | No change. |
| `adapter_registry` | (none) | Remove. Adapter registry is obsolete. |
