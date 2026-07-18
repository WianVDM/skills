---
name: context-reports
description: Provide the canonical vocabulary for shared context reports. Use when a skill produces or consumes context reports, defines report schemas, or needs freshness rules and missing-report handling.
invocation: model-invoked
---

# context-reports

## Purpose

Provide the canonical vocabulary, schema, freshness rules, and missing-report handling for context reports that skills share across a project.

## Type

Vocabulary building block.

## In scope

- Define the canonical directory layout for context reports.
- Define the shared report frontmatter schema.
- Document producer and consumer rules.
- Define freshness and missing-report handling.

## Out of scope

- Writing reports; producing skills own report generation.
- Skill-specific report schemas; individual skills define those and reference this contract for shared conventions.
- Deciding whether a missing report can be regenerated; the consumer judges.

## Canonical directory layout

Reports live at `{context_dir}/{report-type}/{key}.md`, where `{context_dir}` is resolved by `detect-project-context` (canonical default: `{project-root}/.agents/context`).

Organize by report type, not by producing skill, so any skill can find relevant context:

```text
{context_dir}/
├── ticket-research/OC-1234.md
├── state-capture/OC-1234-main.md
├── session-summary/OC-1234-checkpoint.md
└── plan/OC-1234-plan.md
```

## Report schema

Reports use YAML frontmatter (the shared envelope) and a markdown body (skill-specific). See [references/SCHEMA.md](references/SCHEMA.md) for the envelope, repo conventions, consumer declaration format, and the machine-readable schema.

## Producer rules

- Write to the canonical location.
- Include enough metadata for consumers to trust the report: skill, timestamp, scope.
- Keep the body agent-readable: structured headings, concise paragraphs, clear lists.
- Link to related artifacts rather than duplicating them.

## Consumer rules

- Check whether the report exists.
- Validate freshness (below) before trusting it.
- If a fallback path has been approved and recorded in config notes, use it; otherwise note the gap or consult the user.
- Declare consumed reports in `references/DEPENDENCIES.md` and in `skills.json`.

## Freshness and staleness

A report is fresh enough when its timestamp is recent for the domain, the underlying source has not changed since generation, and the producing skill's report schema version is compatible. It is stale when it predates significant changes, comes from an incompatible schema version, or describes a source that no longer exists or has changed materially.

`artifact-freshness` is the operational check: it evaluates branch, commit, timestamps, schema version, and age, and returns a structured verdict. Consumers use it rather than re-implementing freshness heuristics.

Reports are views over data. When a report is generated from tool-collected observations, check the freshness of the underlying observations (see `chainlog`), not just the report.

## Missing reports

Do not fail silently.

| Required? | Response |
| --------- | -------- |
| Required | Stop and consult the user, or run the producing skill if the user has approved that flow. |
| Optional | Proceed, noting in output that the report was not found. |

If the skill can produce the missing report itself, ask first; auto-running another skill has side effects.

## Security

- Prefer read-only inspection when consuming reports from an untrusted project.
- Do not overwrite an existing report without explicit user approval.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Report schema](references/SCHEMA.md)
- The `context-reports` pattern in the skill-standards wiki
