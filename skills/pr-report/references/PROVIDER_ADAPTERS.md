# PR Provider Adapters

Each adapter normalizes PR-platform-specific data into a common shape. The core skill works only with the normalized shape.

## Adapter interface

Every PR provider adapter must support:

| Operation | Input | Output |
|-----------|-------|--------|
| `resolve_pr` | user input, current branch, git remote | PR number, repo, branch, ticket key |
| `fetch_metadata` | PR identifier | title, body, author, state, base, head, url, draft, mergeable |
| `fetch_changed_files` | PR identifier | list of files with status, additions, deletions |
| `fetch_reviews` | PR identifier | top-level reviews with state, reviewer, timestamp |
| `fetch_review_threads` | PR identifier | inline threads with resolution state, comments, line refs |
| `fetch_check_status` | PR identifier | check/run statuses and conclusions |

## Adapter return shape

```yaml
metadata:
  number: 1234
  title: "OC-1234 Fix login flow"
  body: "..."
  author: user
  state: open
  draft: false
  base_ref: origin/development
  head_ref: feature/OC-1234-fix-login
  url: https://github.com/owner/repo/pull/1234
  mergeable: true

changed_files:
  - path: src/auth/login.ts
    status: modified
    additions: 12
    deletions: 4

reviews:
  - id: r1
    reviewer: reviewer-a
    state: CHANGES_REQUESTED
    submitted_at: "2026-06-25T10:00:00Z"

review_threads:
  - id: t1
    is_resolved: false
    path: src/auth/login.ts
    line: 42
    original_line: 42
    comments:
      - id: c1
        author: reviewer-a
        body: "This validation is missing."
        created_at: "2026-06-25T10:00:00Z"
      - id: c2
        author: pr-author
        body: "Resolved. Added validation."
        created_at: "2026-06-25T11:00:00Z"
```

## GitHub adapter notes

- Use GraphQL as the source of truth for `reviewThread.isResolved`.
- Fall back to REST + heuristics only when GraphQL is unavailable.
- For check status, use the GitHub Checks API or equivalent.
- Required status checks should be surfaced separately from optional checks.

## Azure DevOps adapter notes (future)

- Map pull request iteration threads to the `review_threads` shape.
- Use the Azure DevOps REST API for metadata, files, and threads.
- Build status comes from Azure Pipelines via the CI adapter.

## GitLab adapter notes (future)

- Map GitLab diff discussions to `review_threads`.
- Note that GitLab resolves discussions differently; normalize to `is_resolved`.

## Bitbucket adapter notes (future)

- Map Bitbucket pull request comments to threads.
- Use Bitbucket Cloud REST API v2.

## Manual adapter

If `pr_provider: manual`, ask the user to paste:

- PR URL or number
- PR title and description
- List of changed files
- Review comments and inline threads
- Static-analysis findings (optional)
- CI status (optional)
