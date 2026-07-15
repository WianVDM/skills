# Interface

`manual-pr-adapter` implements the `pr-source` interface from `pr-adapter-contract`.

## Input

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

| Field | Required | Description |
|---|---|---|
| `mode` | yes | Input mode. |
| `config.csv_path` | depends | Path to CSV file when `mode` is `csv`. |
| `config.json_path` | depends | Path to JSON file when `mode` is `json`. |
| `config.markdown_path` | depends | Path to Markdown file when `mode` is `markdown`. |
| `config.repo` | no | Repository in `owner/repo` format. |

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

## Operations

Implements the same `pr-source` operations as `github-pr-adapter`:

- `resolve_pr(user_input, repo, current_branch)`
- `fetch_metadata(pr_id)`
- `fetch_changed_files(pr_id)`
- `fetch_reviews(pr_id)`
- `fetch_review_threads(pr_id)`

## Output envelope

The adapter returns the standard `pr-adapter-contract` envelope with `Findings` containing the `pr-source` data.

## Status values

| Status | Meaning |
|---|---|
| `complete` | All provided data collected and normalized. |
| `partial` | Some data provided but not all. |
| `needs_input` | User input required and not yet provided. |
| `blocked` | Provided data is invalid or inconsistent. |
| `skipped` | Not applicable. |

## Rules

- Never ask for data already provided in config or files.
- Collect minimum required data first in interactive mode.
- Normalize all input to `pr-source` shape.
- Handle missing values gracefully.
