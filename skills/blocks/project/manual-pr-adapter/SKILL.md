---
name: manual-pr-adapter
description: Manual PR source adapter that collects PR metadata, changed files, and review feedback from user input, CSV, JSON, or markdown files and returns the normalized pr-source shape.
invocation: model-invoked
depends:
  - pr-adapter-contract
  - worker-contract
---

# manual-pr-adapter

A PR source adapter that collects PR data from user input, files, or pasted content. It is the default fallback when no API-based provider is configured or available.

## Skill type

Tool building block.

## When to use

- The configured PR provider is `manual` or auto-detection finds no supported provider.
- The user wants to report on a PR from Gitea, a custom tool, or an offline review.
- The user has review feedback in a spreadsheet, document, or chat export.

## In scope

- Collect PR metadata from user input or files.
- Collect changed files.
- Collect review threads, top-level reviews, and comments.
- Normalize all input to the `pr-source` adapter shape.
- Support CSV, JSON, and Markdown file formats.

## Out of scope

- Fetching data from APIs itself; the user or conductor supplies any API-obtained data.
- Synthesizing or triaging issues.
- Writing the PR report.

## Input modes

1. **Interactive paste** — Ask the user to paste PR metadata, changed files, and comments.
2. **CSV file** — Read a CSV with a standard column set.
3. **JSON file** — Read a JSON file matching the normalized shape.
4. **Markdown file** — Read a local `.md` file with frontmatter and structured body.
5. **Mixed mode** — Merge data supplied through the other modes (for example, exported API JSON plus pasted comments).

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

Standard worker return contract with the normalized `pr-source` adapter shape.

## Interface operations

- `resolve_pr(user_input, repo, current_branch)` → normalized `pr_number`, `repo`, `branch`, `base`, `ticket_key`, `url`.
- `fetch_metadata(pr_id)` → title, body, author, state, draft, base, head, mergeable, review decision.
- `fetch_changed_files(pr_id)` → list of files with status, additions, deletions, previous path.
- `fetch_reviews(pr_id)` → list of top-level reviews with id, reviewer, state, body, submitted_at.
- `fetch_review_threads(pr_id)` → list of inline threads with path, line, is_resolved, resolution, source_type, comments.

## Completion criteria

- `complete`: All provided data collected and normalized.
- `partial`: Some data provided but not all.
- `needs_input`: User input required and not yet provided.
- `blocked`: Provided data is invalid or inconsistent.
- `skipped`: Not applicable.

## Rules

- Never ask the user for data that is already provided in config or files.
- In interactive mode, collect the minimum required data first, then offer to collect more.
- Normalize all input to the `pr-source` adapter shape before returning.
- Handle missing values gracefully; return `partial` status with notes.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Dependencies](references/DEPENDENCIES.md)
- [Interface](references/INTERFACE.md)
- `pr-adapter-contract` — adapter interface contract
- `worker-contract` — return contract format
