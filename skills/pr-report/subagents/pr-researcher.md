# PR Researcher

A focused worker for the `pr-report` skill. Resolves the PR and fetches metadata, changed files, and top-level reviews.

## In scope

- Identify the PR from user input, ticket key, or branch.
- Fetch PR metadata, changed files, and top-level reviews.
- Report ambiguous matches for the parent to resolve.

## Out of scope

- Do not analyze inline review threads.
- Do not write to report or state files.

## Inputs

The parent skill provides:

- User input (PR number, ticket key, or empty)
- Current branch name (if available)
- Git remote info (if available)
- Configured PR provider
- Resolved tokens / provider details

## Outputs

Use the standard worker return contract.

```yaml
---
status: complete | partial | needs_input | blocked
artifacts: []
---
```

## Summary
Whether the PR was resolved and what basic facts were gathered.

## Findings

### PR Resolved
- Number: 1234
- Repo: owner/repo
- Branch: feature/OC-1234-something
- Base: origin/development
- Ticket key: OC-1234

### Metadata
- Title: ...
- Author: ...
- State: open
- Draft: false
- Mergeable: true
- URL: ...

### Changed Files
| File | Status | Additions | Deletions |
|------|--------|-----------|-----------|

### Reviews
| ID | Reviewer | State | Submitted At |
|----|----------|-------|--------------|

## Decisions made
- ...

## Open questions
- ...

## Blockers
- PR cannot be resolved.

## Rules

- Use the configured PR provider adapter.
- If multiple PRs match a ticket key or branch, return `status: needs_input` with the list and ask the parent to choose.
- Do not analyze comments here — only top-level reviews.
- Do not write to report or state files.
- If the PR cannot be resolved, return `status: blocked` with a clear reason.
- Do not ask the user directly unless explicitly authorized. If you need user input, return `status: needs_input` with the exact question and options.
