---
name: map-ticket-relationships
description: "Map all relationships surrounding a ticket: parent, children, siblings, duplicates, linked tickets, blocked-by/blocks, implementation PRs/branches, original feature for bugs, attachments, and affected files. Use when a skill needs to anchor a ticket in its full context."
invocation: model-invoked
depends:
  - context-reports
  - worker-contract
  - research-ticket
---

# map-ticket-relationships

## Purpose

Build a normalized relationship graph around a ticket. It consumes the raw `related_tickets` and `dev_info` produced by `research-ticket` and enriches them with git-discovered implementation artifacts and affected-file mentions.

## Type

Building-block skill.

## In scope

- Map parent ticket.
- Map child / sub-tickets.
- Map sibling tickets (via shared parent).
- Map duplicate / already-implemented / partially-implemented tickets.
- Map linked / related / blocked-by / blocks tickets.
- Trace original feature for bug tickets (using tracker links, description mentions, or git history).
- Map implementation PRs, branches, and commits.
- Map attachments and external links.
- Map affected files or components mentioned in the ticket.
- Return a normalized relationship graph.
- Use `git` locally to discover branches and commits that mention the ticket key.

## Out of scope

- Do not form assumptions about intent.
- Do not explore the codebase beyond file/component mentions.
- Do not ask the user questions directly.
- Do not decide execution order or recommend next skills.
- Do not call tracker APIs unless explicitly configured (this first version avoids tracker API calls entirely).

## When to use

- `debrief` needs to understand a ticket's full context.
- `debrief-all` needs to build a parent/child hierarchy.
- Any skill needs to know what a ticket is related to.

## Input / output contract

### Input

```yaml
---
ticket_key: OC-4644
ticket_data: { ... } # normalized output from research-ticket
git_state:
  branch: SHB-362
  commit: abc1234
codebase_root: /path/to/project
infer_by_file: true
---
```

| Field           | Required | Description                                                                                                                                  |
| --------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `ticket_key`    | yes      | Ticket/issue key to map.                                                                                                                     |
| `ticket_data`   | yes      | Normalized ticket from `research-ticket`. Must contain `related_tickets`, `dev_info`, `attachments`, and optionally `description`/`summary`. |
| `git_state`     | no       | Current branch/commit. If omitted, local git discovery is skipped.                                                                           |
| `codebase_root` | no       | Root of the codebase. Defaults to the current working directory.                                                                             |
| `infer_by_file` | no       | Infer affected files from ticket description. Default `false`.                                                                               |

### Output

```yaml
---
status: complete
relationships:
  parent: OC-4000
  children: []
  siblings: [OC-4645, OC-4646]
  duplicates: []
  linked: [OC-4500]
  blocked_by: []
  blocks: []
  original_feature:
    ticket: OC-3000
    commit: def5678
    pr: null # reserved; not populated in this version
  implementation:
    prs: ["#123"]
    branches: [feature/OC-4644-auth-guard]
    commits: [abc1234]
  attachments:
    - filename: repro.png
      summary: Screenshot of login redirect
  affected_files:
    - src/app/guards/auth.guard.ts
    - src/app/services/auth.service.ts
gaps: []
---
```

| Status     | Meaning                                     |
| ---------- | ------------------------------------------- |
| `complete` | All available relationships mapped.         |
| `partial`  | Some relationships unavailable; gaps noted. |
| `blocked`  | No tracker or git data available.           |

## Lazy loading

This skill is only invoked when the caller needs relationship context. If the ticket has no linked items and the caller only wants core data, it can be skipped.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## Configuration

See [references/CONFIG_PATTERN.md](references/CONFIG_PATTERN.md).

## Example usage by a conductor

```text
Run map-ticket-relationships with ticket_key OC-4644 and tracker_data from research-ticket.
```

## Notes

- This first version does not call tracker APIs. It uses only the data provided in `ticket_data` plus local `git` inspection.
- Sibling mapping relies on the parent ticket's children. If `ticket_data` does not include explicit siblings, a gap note is returned because this version does not fetch parent data.
- `infer_by_file` performs lightweight, filesystem-validated extraction from the ticket description; it is not a semantic code search.
- `original_feature.pr` is a reserved field. This version makes no tracker or PR-source calls, so it is always returned as null.
- `max_depth` is not a supported input. Relationship depth is not configurable in this version.
