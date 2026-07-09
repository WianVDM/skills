---
name: context-reports
description: Provide the canonical vocabulary for shared context reports. Use when a skill produces or consumes context reports, defines report schemas, or needs freshness rules and missing-report handling.
version: 1.0.1
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [core, building-block, context-reports, shared]
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
- Define freshness and staleness rules.
- Define how to handle missing required and optional reports.

## Out of scope

- This skill does not write reports itself; producing skills own report generation.
- It does not replace skill-specific report schemas or report types; individual skills define those and reference this contract for shared conventions.
- It does not decide whether a missing report can be regenerated; the consumer skill makes that judgment.

## When to use

- A skill needs to read or write context reports in a standard location.
- A skill author wants to align report metadata, freshness checks, or missing-report handling with the shared convention.
- A skill needs to reference the canonical directory layout or report envelope.

## Canonical directory layout

Reports live at:

```text
{project-root}/.agents/context/{report-type}/{key}.md
```

Organize by report type, not by producing skill. This makes it easy for any skill to find relevant context.

Examples:

```text
.agents/context/
├── ticket-research/OC-1234.md
├── state-capture/OC-1234-main.md
├── session-summary/OC-1234-checkpoint.md
└── plan/OC-1234-plan.md
```

## Report schema

Reports use frontmatter and a markdown body. The frontmatter is the shared envelope; the body is skill-specific. A skill must document what reports it produces and what reports from other skills it consumes.

For the full schema and consumer declaration format, see [`references/SCHEMA.md`](references/SCHEMA.md). A machine-readable JSON Schema is available at [`references/context-report-schema.json`](references/context-report-schema.json).

## Producer/consumer rules

When a skill produces a report:

- Write it to the canonical location.
- Include enough metadata for consumers to trust it: skill name, version, timestamp, scope.
- Keep the body agent-readable: structured headings, concise paragraphs, clear lists.
- Link to related artifacts rather than duplicating them.

When a skill consumes a report:

- Check whether the report exists.
- Validate freshness against timestamps and underlying changes.
- If a fallback path has been approved and recorded in config notes, use it. Otherwise, note the gap or consult the user.

A consuming skill should declare the reports it needs in `references/DEPENDENCIES.md` or in a `consumes` section in `SKILL.md` frontmatter. See [`references/SCHEMA.md`](references/SCHEMA.md) for the declaration format.

## Freshness and staleness

A report is fresh enough if:

- Its timestamp is recent relative to the rate of change in the domain.
- The underlying source has not changed since the report was generated.
- The skill's version matches the consumer's expectations.

A report is stale if:

- It predates significant code changes.
- It was produced by an older skill version with an incompatible schema.
- The source it describes no longer exists or has changed materially.

Skills should document how they determine freshness and what they do when a report is stale.

## Missing reports

Do not fail silently. The right response depends on whether the report is required or optional:

| Required? | Response |
|-----------|----------|
| Required | Stop and consult the user, or run the producing skill if the user has approved that flow. |
| Optional | Proceed, noting in output that the report was not found. |

If a skill can produce a missing report itself, ask before doing so. Auto-running another skill can have side effects the user did not expect.

## Security

- Prefer read-only inspection when consuming reports from an untrusted project.
- Do not overwrite an existing report without explicit user approval.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `docs/skill-standards/patterns/context-reports.md`
- [`references/SCHEMA.md`](references/SCHEMA.md)
