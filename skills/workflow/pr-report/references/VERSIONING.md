---
name: pr-report-versioning
description: Versioning policy for the pr-report skill and its produced reports/state.
metadata:
  author: Wian van der Merwe
  tags: [pr-report, versioning, schema]
  version: "1.0.0"
---

# Versioning

`pr-report` is a workflow conductor that produces reports and state files consumed by other skills and by the user. This document defines how the skill is versioned and how report/state schema changes are handled.

## Version concepts

| Concept | Location | Changes when |
|---|---|---|
| **Skill version** | `metadata.version` in `SKILL.md` | Orchestration, workflow, adapter contract, or triage behavior changes. |
| **Report / state schema version** | `version` field in report and state frontmatter | Columns, sections, frontmatter fields, or delta classifications are added, removed, or renamed. |

A single release may bump one, both, or neither.

## Current versions

- Skill version: `1.0.0`
- Report/state schema version: `1`

## Breaking changes

A breaking change requires a major bump to the affected version:

- Removing or renaming a report section or frontmatter field.
- Changing the meaning of an existing field without renaming it.
- Changing the adapter interface contract.
- Changing the return format of a subagent or building block consumed by other skills.

Non-breaking changes include:

- Adding new optional report sections or fields.
- Adding new adapters or workflow steps that do not change existing output.
- Clarifying wording without changing behavior.

## Migration path

When loading an existing state or report file:

1. Read its `version` field.
2. If the version matches the current schema, use it directly.
3. If the version is older but backward compatible, read what is present and treat missing fields as empty/default.
4. If the version is older and not backward compatible, mark the file as stale, archive it, and write a new file with the current schema.

Append-only history tables (comment history, session history, triage decisions) are migrated into the new schema when possible rather than discarded.

## Config schema migration

When the config schema changes:

1. Load the existing config and validate it against the current schema.
2. Map known old keys to new keys automatically when the intent is unambiguous.
3. If an old key has no clear equivalent, report the conflict and ask the user.
4. Persist the migrated config under the new schema and append a `decision` note recording the migration.

## Deprecation

Deprecated behavior is documented in this file and supported for a reasonable transition period. The skill emits a note when deprecated config keys or report fields are used.

## Archive path

Stale artifacts are moved to:

```text
{context_dir}/pr-report/archive/{key}-{artifact}-{old-version}.md
```

The new artifact records the archive path in `archived_artifacts` or in the state notes.
