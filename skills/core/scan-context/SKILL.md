---
name: scan-context
description: "Discover related context reports in a project's context directory by ticket key, project, branch, or report type. Use when a skill needs to find prior baselines, handoffs, debriefs, or other shared reports."
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [core, building-block, context, reports, discovery]
allowed-tools:
  - read
  - bash
---

# scan-context

## Purpose

Find related context reports in `{context_dir}/` without knowing the producer skill name. It matches by report type, ticket key, project, branch, and frontmatter fields, then ranks results by relevance and freshness.

## Type

Building block.

## In scope

- Scan `{context_dir}/` subdirectories for `.md` reports.
- Filter by report type (subdirectory name), e.g. `baseline`, `handoff`, `debrief`.
- Match reports by `ticket_key`, `project`, or `branch`.
- Rank matches by relevance: exact ticket key match > branch match > project match, with recency as a tiebreaker.
- Flag reports as fresh or stale using a configurable age threshold.
- Return a ranked list of report metadata without reading full report bodies.

## Out of scope

- Do not read the full content of every report unless it is matched as relevant.
- Do not interpret, synthesize, or validate the body content of discovered reports.
- Do not ask the user questions.
- Do not decide which reports are actionable beyond the ranking rules.

## When to use

- `debrief` wants to know if a baseline or handoff report already exists for a ticket.
- `debrief-all` wants to find existing child debriefs.
- Any conductor or skill wants to discover prior context before producing a new report.

## Input / output contract

### Input

The skill accepts a JSON object via stdin when invoked as a script:

```json
{
  "context_dir": "/path/to/.agents/context",
  "ticket_key": "OC-4644",
  "project": "OC",
  "branch": "feature/OC-4644",
  "report_types": ["baseline", "handoff", "debrief"],
  "artifact_freshness_hours": 24,
  "top_n": 10
}
```

| Field | Required | Description |
|---|---|---|
| `context_dir` | yes | Absolute or relative path to the context directory. |
| `ticket_key` | no | Ticket or report key to match exactly. |
| `project` | no | Project key to match against ticket key prefixes. |
| `branch` | no | Branch name to match against report frontmatter. |
| `report_types` | no | List of report type subdirectory names to scan. Defaults to all subdirectories. |
| `artifact_freshness_hours` | no | Age threshold in hours for freshness. Defaults to `24`. |
| `top_n` | no | Maximum number of reports to return. Defaults to `10`. |

### Output

The skill returns a JSON object:

```json
{
  "status": "complete",
  "reports": [
    {
      "path": "/path/to/.agents/context/baseline/OC-4644.md",
      "type": "baseline",
      "ticket_key": "OC-4644",
      "branch": "feature/OC-4644",
      "generated_at": "2026-07-08T10:00:00Z",
      "relevance": "High",
      "matched_by": "ticket_key",
      "fresh": true
    }
  ]
}
```

| Field | Description |
|---|---|
| `status` | `complete`, `empty`, or `error`. |
| `reports` | Ranked list of matching report metadata. |
| `path` | Absolute path to the report file. |
| `type` | Report type inferred from the subdirectory name. |
| `ticket_key` | Ticket key from frontmatter (`key`, `ticket_key`, or `ticket`), when present. |
| `branch` | Branch from frontmatter, when present. |
| `generated_at` | ISO 8601 timestamp from frontmatter (`generated_at`, `baselined_at`, or `updated_at`), when present. |
| `scope` | Scope from frontmatter, when present. |
| `method` | Method from frontmatter, when present. |
| `parent` | Parent reference from frontmatter, when present. |
| `relevance` | `High`, `Medium`, or `Low`. |
| `matched_by` | `ticket_key`, `branch`, `project`, or `recency`. |
| `fresh` | `true` if the report is newer than the freshness threshold. |

## Steps

1. **Accept and validate input.** Ensure `context_dir` exists and is a directory.
2. **Discover report directories.** Use the requested `report_types` or scan all immediate subdirectories of `context_dir`.
3. **Collect `.md` files.** Skip hidden directories and files.
4. **Parse frontmatter.** Extract `key`, `ticket_key`, `ticket`, `branch`, `generated_at`, `baselined_at`, `updated_at`, `scope`, `method`, and `parent` from each report. PyYAML is used when available; otherwise a vendored fallback parser handles the same scalar and nested fields.
5. **Match and rank.** Score each report by match type and recency.
6. **Apply freshness.** Compare `generated_at` against the configured threshold.
7. **Return results.** Emit the top `top_n` reports as JSON.

## Ranking

Relevance is determined in this order:

1. **High** — exact ticket key match (`ticket_key` matches the report's `key`, `ticket_key`, or `ticket`).
2. **Medium** — branch match (`branch` matches the report's `branch`).
3. **Low** — project match (report key begins with the project prefix).

Within the same relevance tier, newer reports rank higher. Reports with no direct match are not returned.

## Security

- This skill is read-only. It does not create, modify, or delete files.
- It only inspects report frontmatter; it does not execute report bodies.
- Hidden directories and files are skipped.

## Dependencies

`scan-context` is a deterministic Python script. The preferred frontmatter parser is PyYAML; if it is unavailable, the script falls back to a vendored parser and discloses the degraded source because YAML coverage is reduced.

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `context-reports` (recommended convention)
