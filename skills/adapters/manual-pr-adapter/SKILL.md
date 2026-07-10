---
name: manual-pr-adapter
description: Manual PR source adapter for pr-report. Collects PR metadata, changed files, and review feedback from user input, CSV, JSON, or markdown files.
invocation: model-invoked
metadata:
  tags: [adapter, pr-source, manual, building-block]
  author: Wian van der Merwe
  version: "1.0.1"
---

# Manual PR Adapter

A PR source adapter that collects PR data from user input, files, or pasted content. It is the default fallback when no API-based provider is configured or available.

## Purpose

Make `pr-report` work with unsupported tools, manual processes, or teams that do not use a mainstream PR platform.

## Type

Tool building block. Implements the `pr-source` adapter interface defined in the `pr-adapter-contract` skill.

## In scope

- Collect PR metadata from user input or files.
- Collect changed files.
- Collect review threads, top-level reviews, and comments.
- Normalize all input to the `pr-source` adapter shape.
- Support CSV, JSON, and Markdown file formats.

## Out of scope

- This adapter does not fetch data from APIs.
- It does not synthesize or triage issues. That is the conductor's job.
- It does not write the PR report.

## When to use

- The configured PR provider is `manual` or auto-detection finds no supported provider.
- The user wants to report on a PR from Gitea, a custom tool, or an offline review.
- The user has review feedback in a spreadsheet, document, or chat export.

## Input modes

1. **Interactive paste** — Ask the user to paste PR metadata, changed files, and comments.
2. **CSV file** — Read a CSV with a standard column set.
3. **JSON file** — Read a JSON file matching the normalized shape.
4. **Markdown file** — Read a local `.md` file with frontmatter and structured body.
5. **Mixed mode** — Combine API data with manual additions.

## Inputs

```yaml
---
mode: interactive | csv | json | markdown | mixed
config:
  csv_path: ./pr-data.csv
  json_path: ./pr-data.json
  markdown_path: ./pr-data.md
  repo: owner/repo
---
```

## Outputs

Standard worker return contract with the normalized `pr-source` adapter shape:

```yaml
---
status: complete | partial | needs_input | blocked
---

## Summary
How the PR data was collected and normalized.

## Findings
### PR Resolved
- Number: 1234
- Repo: owner/repo
- Branch: feature/OC-1234-fix
- Base: origin/main
- Ticket key: OC-1234

### Metadata
- Title: Fix login flow
- Author: user
- State: open
- Draft: false

### Changed Files
| File | Status | Additions | Deletions |

### Reviews
| ID | Reviewer | State | Submitted At |

### Review Threads
| Thread ID | Path | Line | Is Resolved | Comments |

## Decisions made
- Source selected because `adapters.pr.source` was `manual-pr-adapter`.
- CSV format detected; parsed 5 comments.

## Open questions
- ...

## Blockers
- User has not provided PR metadata.
```

## CSV format

```csv
id,author,body,file,line,severity,source_type,created_at
r1,reviewer-a,Approve with changes,,,approved,human_reviewer,2026-07-07T10:00:00Z
c1,reviewer-a,Missing validation,src/auth/login.ts,42,required_to_resolve,human_reviewer,2026-07-07T10:00:00Z
c2,sonarqube,Remove unused import,src/auth/login.ts,5,required,static_analysis,2026-07-07T10:05:00Z
```

## Markdown file format

```markdown
---
pr_number: 1234
repo: owner/repo
branch: feature/OC-1234-fix
base: origin/main
title: Fix login flow
---

## Changed Files
- src/auth/login.ts (modified)

## Reviews
- id: r1
  reviewer: reviewer-a
  state: CHANGES_REQUESTED

## Comments
- id: c1
  author: reviewer-a
  body: "Missing validation."
  file: src/auth/login.ts
  line: 42
  severity: required_to_resolve
  source_type: human_reviewer
```

## Rules

- Never ask the user for data that is already provided in config or files.
- In interactive mode, collect the minimum required data first, then offer to collect more.
- Normalize all input to the `pr-source` adapter shape before returning.
- Handle missing values gracefully; return `partial` status with notes.

## Dependencies

- `worker-contract` skill.
- `read`, `write`, `bash` tools.
- Python 3.x for CSV/JSON parsing if needed.

## References

- `pr-adapter-contract` skill — adapter interface contract
- `pr-report/references/ADAPTER_ARCHITECTURE.md` — high-level adapter architecture
