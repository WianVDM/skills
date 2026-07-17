# Report schema

Context reports use YAML frontmatter (the shared envelope) and a markdown body (skill-specific).

## Machine-readable schema

[`context-report-schema.json`](context-report-schema.json) is the **embedded fallback** mirror of the canonical context-report schema in the skill-standards wiki.

Precedence:

1. When the standards are resolvable (configured `standards_path` or `resolve-standards-path.py`), validate against the canonical schema.
2. When they are not, validate against this copy.

The two files are kept byte-identical by a sync test in this repo. A consuming conductor that falls back to this copy discloses degraded mode; the consumer owns the warning, this block never prompts.

`additionalProperties` is `true`: skills may add skill-specific fields.

## Envelope

```yaml
---
skill: ticket-research
version: 1
key: OC-1234
generated_at: 2026-06-26T08:42:00Z
summary: "One-sentence synthesis."
artifacts:
  - .agents/context/state-capture/OC-1234-main.md
---
```

Required: `skill`, `key`, `generated_at` (ISO 8601).
Optional in the envelope: `version` (string or integer), `summary`, `artifacts`.

## Repo conventions

These optional fields are conventional across this repository's skills. They are not part of the shared envelope; the envelope allows them via `additionalProperties`.

| Field | Used by | Meaning |
|---|---|---|
| `ticket` | debrief, ticket-research | Ticket key the report is about. |
| `scope` | baseline | Scope identifier (`feature`, `route`, `bug`, `module`). |
| `branch` | debrief, baseline | Branch the report was produced on. |
| `commit` | debrief, baseline | Commit hash at production time. |
| `method` | baseline | Capture method (`ui-browser`, `api-http`, `test-runner`, `code-snapshot`, `manual`). |
| `updated_at` | debrief | ISO 8601 last-update timestamp. |
| `baselined_at` | baseline | ISO 8601 capture timestamp. |
| `parent` | debrief | Parent ticket key. |
| `parent_debrief` | debrief | Path to the parent debrief report. |

Skills may add further fields that do not conflict with the envelope. Each skill documents its full report schema and points to this shared envelope for the canonical fields.

## Consumer declaration

Declare produced and consumed reports in `references/DEPENDENCIES.md` for human readers and in `skills.json` for machines. Example:

```markdown
## Consumed reports

- `{context_dir}/ticket-research/{key}.md`
- `{context_dir}/state-capture/{key}-{branch}.md`
```

Consumers must handle absence gracefully: fall back to an approved alternative, note the gap, or consult the user.
