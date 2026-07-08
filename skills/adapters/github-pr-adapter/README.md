# github-pr-adapter

GitHub PR source adapter for `pr-report`.

## Purpose

Fetch PR metadata, changed files, reviews, and inline review threads from GitHub and normalize them to the standard `pr-source` adapter shape.

## When to use

- The configured PR source is GitHub.
- The git remote points to a GitHub repository.

## Inputs

Repo identifier, GitHub API token, and optional API/GraphQL URLs.

## Outputs

Normalized PR data in the `pr-source` adapter shape.

## Dependencies

- `token-resolver` for token resolution.
- Network access to the GitHub API.
