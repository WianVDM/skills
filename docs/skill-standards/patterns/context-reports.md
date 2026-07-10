# Context reports

Skills share context by reading and writing reports in a well-known location. A shared context layer lets skills compose without being tightly coupled.

---

## Context directory

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

---

## Report schema

Reports use frontmatter and markdown body:

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

A JSON Schema for context report frontmatter is maintained at `schemas/context-report.schema.json`.

A skill must document:

- What reports it produces.
- What reports from other skills it consumes.
- The schema and freshness expectations.

---

## Producing reports

When a skill produces a report:

- Write it to the canonical location.
- Include enough metadata for consumers to trust it: skill name, version, timestamp, scope.
- Keep the body agent-readable: structured headings, concise paragraphs, clear lists.
- Link to related artifacts rather than duplicating them.

---

## Consuming reports

When a skill consumes a report:

- Check whether the report exists.
- Validate freshness against timestamps and underlying changes.
- Do not fail silently if a required report is missing.
- If a fallback path has been approved and recorded in config notes, use it. Otherwise, note the gap or consult the user.

Treat reports as potentially stale. A report from last week may not reflect the current codebase.

---

## Cross-skill consumption

A skill should declare the reports it consumes. The canonical place is `references/DEPENDENCIES.md` or a `dependencies` section in `SKILL.md` frontmatter.

Example:

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

A consuming skill must handle absence gracefully: fall back to an approved alternative, note the gap, or consult the user.

---

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

---

## Missing reports

Do not fail silently. The right response depends on whether the report is required or optional:

| Required? | Response |
|-----------|----------|
| Required | Stop and consult the user, or run the producing skill if the user has approved that flow. |
| Optional | Proceed, noting in output that the report was not found. |

If a skill can produce a missing report itself, ask before doing so. Auto-running another skill can have side effects the user did not expect.

---

## Shared context conventions

To avoid duplication, extract shared context conventions into a building-block skill or shared reference file. Individual skills should not each explain the context directory layout.

A shared `context-reports` skill can define:

- The canonical directory layout.
- The report frontmatter schema.
- Freshness rules.
- How to handle missing reports.

Individual skills then reference it.

---

## Research basis

- The **context reports** pattern (structured artifacts shared between skills) is our own, but it is strongly supported by the research on composition, memory, and the need for skills to share findings without tight coupling.
- The `.agents/context/{report-type}/{key}.md` layout is our own convention, aligned with the research emphasis on well-known locations for shared context.
- The report schema (frontmatter with skill, version, key, generated_at, summary, artifacts) is our own format.
- The **freshness** rules and the handling of missing reports are our own practices, informed by the research finding that stale reports can mislead the agent.
- The recommendation to extract shared context conventions into a vocabulary building block is our own, aligned with the building-block pattern.
