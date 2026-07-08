# github-actions-adapter

CI source adapter for `pr-report`.

## Purpose

Fetch GitHub Actions check runs and job-log summaries for a PR and return the normalized `ci-source` shape.

## When to use

When `pr-report` config points `adapters.ci.source` to `github-actions-adapter` and the repository runs GitHub Actions.

## Inputs

| Field | Description |
|---|---|
| `repo` | Repository slug (`owner/repo`). |
| `head_commit_sha` | Commit SHA at the PR head. |
| `token` | Resolved GitHub token (via `token-resolver`). |
| `required_checks` | Optional list of required check names. |

## Outputs

Normalized `ci-source` data:

- `status`: `passing`, `failing`, `mixed`, or `unknown`.
- `checks`: array of check objects with name, status, conclusion, URL, required flag, and summary.
- `log_summary`: summary, full log URL, and error lines for failing checks.

See `SKILL.md` for the full interface and worker-return-contract example.
