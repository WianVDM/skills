# Report schema

Context reports use YAML frontmatter and a markdown body. The frontmatter is the shared envelope; the body is skill-specific.

## Machine-readable schema

A JSON Schema for the shared envelope is provided in [`context-report-schema.json`](context-report-schema.json). Consumers can validate report frontmatter against it; skills may add additional skill-specific fields because `additionalProperties` is `true`.

## Example

```yaml
---
skill: skill-name
version: 1.0.0
key: OC-1234
generated_at: 2026-06-26T08:42:00Z
summary: "One-sentence synthesis."
artifacts:
  - .agents/context/state-capture/OC-1234-main.md
---
```

## Required fields

- `skill` — name of the producing skill.
- `version` — version of the producing skill.
- `key` — report identifier, usually matching the ticket or session key.
- `generated_at` — ISO 8601 timestamp.

## Optional fields

- `summary` — one-sentence synthesis.
- `artifacts` — list of related report paths.
- `ticket` — ticket key the report is about (used by `debrief` and `ticket-research`).
- `scope` — scope identifier, e.g., `feature`, `route`, `bug`, `module` (used by `baseline`).
- `branch` — branch the report was produced on (used by `debrief` and `baseline`).
- `commit` — commit hash the report was produced at (used by `debrief` and `baseline`).
- `method` — capture method, e.g., `ui-browser`, `api-http`, `test-runner`, `code-snapshot`, `manual` (used by `baseline`).
- `updated_at` — ISO 8601 timestamp of the last update (used by `debrief`).
- `baselined_at` — ISO 8601 timestamp when the baseline was captured (used by `baseline`).
- `parent` — parent ticket key, if any (used by `debrief`).
- `parent_debrief` — path to the parent debrief report (used by `debrief`).

Individual skills may add additional skill-specific fields as long as they do not conflict with the required envelope fields. Each skill must document its full report schema and point to this shared envelope for the canonical fields.

## Consumer declaration

A consuming skill should declare the reports it needs in `references/DEPENDENCIES.md` or in a `consumes` section in `SKILL.md` frontmatter.

```yaml
---
name: project-orchestration
consumes:
  - .agents/context/ticket-research/{key}.md
  - .agents/context/state-capture/{key}-{branch}.md
requires:
  - ticket-research
  - state-capture
---
```
