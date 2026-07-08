---
name: github-pr-adapter
description: GitHub PR source adapter for pr-report. Fetches PR metadata, changed files, reviews, and inline review threads via the GitHub API.
license: Proprietary
invocation: model-invoked
metadata:
  tags: [adapter, pr-source, github, building-block]
  author: Wian van der Merwe
  version: "1.0.1"
---

# GitHub PR Adapter

A PR source adapter that fetches PR data from GitHub and normalizes it to the `pr-source` adapter shape.

## Purpose

Provide `pr-report` with PR metadata, changed files, reviews, and inline review threads from GitHub.

## Type

Tool building block. Implements the `pr-source` adapter interface defined in the `pr-report` adapter contract (`pr-adapter-contract` building block).

## In scope

- Resolve a PR from user input, ticket key, branch, or repo context.
- Fetch PR metadata (title, body, author, state, draft, base, head, mergeable, review decision).
- Fetch changed files with status, additions, and deletions.
- Fetch top-level reviews.
- Fetch inline review threads with resolution state and comments.
- Normalize all data to the `pr-source` adapter shape.

## Out of scope

- CI / build status (use `github-actions-adapter`).
- Static-analysis findings (use `sonarcloud-adapter` or `sonarqube-adapter`).
- Issue tracker scope (use `jira-adapter` or `github-issues-adapter`).
- Synthesizing or triaging issues.

## When to use

- The configured PR source is GitHub.
- The git remote points to a GitHub repository.
- The user provides a GitHub PR URL or number.

## Inputs

```yaml
---
repo: owner/repo
config:
  token: ${GITHUB_TOKEN}
  api_url: https://api.github.com
  graphql_url: https://api.github.com/graphql
---
```

The token is resolved by the `token-resolver` building block before this adapter is invoked.

## Outputs

Standard worker return contract with the `pr-source` adapter shape.

## Interface operations

- `resolve_pr(user_input, repo, current_branch)` → normalized `pr_number`, `repo`, `branch`, `base`, `ticket_key`, `url`.
- `fetch_metadata(pr_id)` → title, body, author, state, draft, base, head, mergeable, review decision.
- `fetch_changed_files(pr_id)` → list of files with status, additions, deletions, previous path.
- `fetch_reviews(pr_id)` → list of top-level reviews with id, reviewer, state, body, submitted_at.
- `fetch_review_threads(pr_id)` → list of inline threads with path, line, is_resolved, resolution, source_type, comments.

## Completion criteria

- `complete`: PR resolved and all requested metadata, files, reviews, and threads normalized in the `pr-source` shape.
- `partial`: Some data fetched but not all (e.g., GraphQL unavailable, only REST data returned); missing items are listed.
- `needs_input`: Token is missing or invalid, or the PR cannot be resolved unambiguously.
- `blocked`: API is unreachable or the repository/PR is inaccessible even with a valid token.
- `skipped`: Not applicable for this adapter.

## Implementation notes

- Use the GitHub GraphQL API as the source of truth for `reviewThread.isResolved`.
- Fall back to the REST API plus heuristics when GraphQL is unavailable.
- For check status, return an empty list; the `github-actions-adapter` provides CI data.

## Rules

- Do not log the token.
- Return `needs_input` if the token is missing or invalid, or if the PR cannot be resolved unambiguously.
- Return `blocked` if the API is unreachable or the repository is inaccessible even with a valid token.
- Normalize all timestamps to ISO 8601 UTC.

## Dependencies

- `worker-contract` skill.
- `token-resolver` skill for token resolution.
- Network access to the GitHub API.
- Python 3.x or equivalent for API calls.

## References

- `pr-adapter-contract` skill — adapter interface contract
- `pr-report/references/ADAPTER_ARCHITECTURE.md` — high-level adapter architecture
