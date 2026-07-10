---
name: github-actions-adapter
description: CI source adapter for the pr-report conductor. Fetches GitHub Actions check runs and job-log summaries and returns the normalized ci-source shape.
invocation: model-invoked
metadata:
  tags: [pr-report, adapter, ci-source, github-actions, building-block]
  author: Wian van der Merwe
  version: "1.0.1"
---

# github-actions-adapter

Tool building block that implements the `ci-source` adapter interface for `pr-report`. It translates GitHub Actions API data into the normalized CI/build shape expected by the conductor.

## In scope

- Fetch GitHub Actions check runs for a PR head commit.
- Summarize failing job logs into normalized `error_lines` and `summary` fields.
- Map GitHub Actions status/conclusion values to the normalized `ci-source` output shape.
- Return the adapter envelope status (`complete`, `partial`, `needs_input`, `blocked`, `skipped`) and confidence.
- Accept configuration provided by `pr-report` (`repo`, `commit_sha`, `token`, `required_checks`, etc.).

## Out of scope

- Synthesizing or triaging issues from CI output. The conductor owns that.
- Writing the PR report. The conductor owns that.
- Fixing code, rerunning jobs, or mutating GitHub Actions state.
- Handling non-GitHub CI systems (use a different adapter).
- Resolving tokens directly. The shared `token-resolver` building block resolves `GITHUB_TOKEN`.

## When to use

Use this adapter when the `pr-report` configuration selects it as the CI source:

```yaml
adapters:
  ci:
    source: github-actions-adapter
    config:
      repo: owner/repo
      token: ${GITHUB_TOKEN}
```

## Interface operations

Implements the `ci-source` interface from `pr-adapter-contract`:

- `fetch_check_runs(pr_id, head_commit_sha)` → normalized `{ status, checks }`
- `fetch_job_log_summary(failing_check)` → normalized `{ summary, full_log_url, error_lines }`

## Example input

```yaml
config:
  repo: owner/repo
  head_commit_sha: abc123def456
  token: ${GITHUB_TOKEN}
  required_checks:
    - "Run tests"
    - "Lint"
```

## Example output (worker return contract)

```yaml
---
status: complete
artifacts: []
---

## Summary
Fetched 4 GitHub Actions check runs for owner/repo@abc123def456; 1 required check failed.

## Findings
adapter_role: ci-source
status: failing
checks:
  - name: "Run tests"
    status: completed
    conclusion: failure
    url: https://github.com/owner/repo/actions/runs/123
    is_required: true
    summary: "3 tests failed in AuthService."
  - name: "Lint"
    status: completed
    conclusion: success
    url: https://github.com/owner/repo/actions/runs/124
    is_required: true
    summary: "No lint errors."

log_summary:
  summary: "Error: expected 200 but got 401 at src/auth/login.test.ts:42"
  full_log_url: https://github.com/owner/repo/actions/runs/123/logs
  error_lines:
    - "FAIL src/auth/login.test.ts:42"
    - "Expected: 200"
    - "Received: 401"
```

## Completion criteria

- `complete`: All check runs for the head commit fetched and normalized, including a log summary for any failing required check.
- `partial`: Some check runs or log summaries are unavailable; missing items are listed.
- `needs_input`: Token is missing or invalid.
- `blocked`: Repository or commit is unreachable, or the API returns a persistent error.
- `skipped`: Not applicable for this adapter.

## Rules

- Return the normalized `ci-source` shape, not raw GitHub Actions API responses.
- Never log or expose the resolved token.
- Distinguish `complete`, `partial`, `needs_input`, `blocked`, and `skipped` clearly.
- If the token is missing or invalid, return `needs_input` with the required env-var name.
- If the repository or commit is unreachable, return `blocked` with the HTTP error.
- If the API returns partial data, return `partial` and list the missing checks.
- Mark `is_required: true` only for checks listed in `required_checks` config. If branch protection rules are also fetched, include them, but declare that capability in the adapter dependencies.
- Keep `error_lines` short and relevant; the conductor may truncate very long logs.
- Reference the adapter contract at `pr-adapter-contract` for envelope shape and status semantics.

## References

- `pr-adapter-contract` skill — adapter interface contract
- `pr-report/references/ADAPTER_ARCHITECTURE.md` — high-level adapter architecture
- `worker-contract` skill — return contract format
- `token-resolver` building block — token resolution
