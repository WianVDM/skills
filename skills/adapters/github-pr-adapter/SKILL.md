---
name: github-pr-adapter
description: GitHub PR source adapter for pr-report. Fetches PR metadata, changed files, reviews, and inline review threads via the GitHub API.
license: Proprietary
invocation: model-invoked
metadata:
  tags: [adapter, pr-source, github, building-block]
  author: Wian van der Merwe
  version: "1.0.0"
  verification_level: declared
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

## Implementation notes

- Use the GitHub GraphQL API as the source of truth for `reviewThread.isResolved`.
- Fall back to the REST API plus heuristics when GraphQL is unavailable.
- For check status, return an empty list; the `github-actions-adapter` provides CI data.

## Rules

- Do not log the token.
- Return `blocked` if the token is invalid or the API is unreachable.
- Return `needs_input` if the PR cannot be resolved unambiguously.
- Normalize all timestamps to ISO 8601 UTC.

## Dependencies

- `worker-contract` skill.
- `token-resolver` skill for token resolution.
- Network access to the GitHub API.
- Python 3.x or equivalent for API calls.

## References

- `pr-adapter-contract` skill — adapter interface contract
- `pr-report/references/ADAPTER_ARCHITECTURE.md` — high-level adapter architecture
