---
name: github-actions-adapter
description: CI source adapter that fetches GitHub Actions check runs and job-log summaries and returns the normalized ci-source shape.
invocation: model-invoked
depends:
  - pr-adapter-contract
  - worker-contract
  - token-resolver
---

# github-actions-adapter

Tool building block that implements the `ci-source` adapter interface. It translates GitHub Actions API data into the normalized CI/build shape.

## Skill type

Tool building block.

## When to use

- The configured CI source is GitHub Actions.
- The repository uses GitHub Actions workflows.

## In scope

- Fetch GitHub Actions check runs for a PR head commit.
- Summarize failing job logs into normalized `error_lines` and `summary` fields.
- Map GitHub Actions status/conclusion values to the normalized `ci-source` output shape.
- Return the adapter envelope status and confidence.

## Out of scope

- Synthesizing or triaging issues from CI output.
- Writing the PR report.
- Fixing code, rerunning jobs, or mutating GitHub Actions state.
- Handling non-GitHub CI systems.
- Resolving tokens directly.

## Inputs

```yaml
config:
  repo: owner/repo
  head_commit_sha: abc123def456
  token: ${GITHUB_TOKEN}
  required_checks:
    - "Run tests"
    - "Lint"
```

## Outputs

Standard worker return contract with the `ci-source` adapter shape.

## Interface operations

- `fetch_check_runs(pr_id, head_commit_sha)` → normalized `{ status, checks }`.
- `fetch_job_log_summary(failing_check)` → normalized `{ summary, full_log_url, error_lines }`.

## Completion criteria

- `complete`: All check runs fetched and normalized, including log summaries for failing required checks.
- `partial`: Some check runs or log summaries unavailable; missing items listed.
- `needs_input`: Token missing or invalid.
- `blocked`: Repository or commit unreachable, or API returns persistent error.
- `skipped`: Not applicable.

## Rules

- Return the normalized `ci-source` shape, not raw API responses.
- Never log or expose the resolved token.
- Distinguish `complete`, `partial`, `needs_input`, `blocked`, and `skipped` clearly.
- Mark `is_required: true` only for checks listed in `required_checks` config.
- Keep `error_lines` short and relevant.
- Fetch GitHub Actions results from the check-runs API only. Commit statuses (the legacy statuses API, exposed by tools like `get_pull_request_status`) are a different channel and do not include Actions checks; a tool that only exposes statuses will miss them.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Dependencies](references/DEPENDENCIES.md)
- [Interface](references/INTERFACE.md)
- `pr-adapter-contract` — adapter interface contract
- `worker-contract` — return contract format
- `token-resolver` — token resolution
