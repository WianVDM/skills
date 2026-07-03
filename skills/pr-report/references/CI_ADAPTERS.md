# CI / Build Adapters

The CI adapter fetches the status of checks, pipelines, or builds associated with the PR. If `fetch_logs` is enabled, it also summarizes failing job logs.

## Adapter interface

| Operation | Input | Output |
|-----------|-------|--------|
| `fetch_check_runs` | PR identifier, commit SHA | list of checks with name, status, conclusion, url |
| `fetch_job_log_summary` | failing check | concise failure summary and link to full log |

## Check run shape

```yaml
check_runs:
  - name: "Run tests"
    status: completed
    conclusion: failure
    url: https://github.com/owner/repo/actions/runs/123
    is_required: true
    summary: "3 tests failed in AuthService tests."
```

## Required vs optional checks

Required checks are blockers if failing. Optional checks are reported but do not block merge.

## Log summarization rules

When `fetch_logs: true`:

1. Identify the most recent failing run for each required failing check.
2. Fetch the job log.
3. Extract error messages, assertion failures, stack traces, and compilation errors.
4. Truncate to a readable summary (e.g., first 20 error lines + last 20 lines).
5. Store the full log URL; do not paste the entire log into the report.

## GitHub Actions adapter notes

- Use the GitHub Checks API or Actions API to list runs for the PR's head commit.
- Determine required checks from branch protection rules if available.
- Fetch logs via the Actions logs endpoint.

## Azure Pipelines adapter notes (future)

- Query the pull request's build validation policies.
- Fetch failing step logs from Azure DevOps.

## GitLab CI adapter notes (future)

- Fetch pipeline status for the PR's source branch.
- Summarize failing job traces.

## Jenkins adapter notes (future)

- Query the PR-specific Jenkins job or multibranch pipeline.
- Fetch the console output of the latest failing build.
