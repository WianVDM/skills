# Interface

`github-actions-adapter` implements the `ci-source` interface from `pr-adapter-contract`.

## Input

```yaml
config:
  repo: owner/repo
  head_commit_sha: abc123def456
  token: ${GITHUB_TOKEN}
  required_checks:
    - "Run tests"
    - "Lint"
```

| Field | Required | Description |
|---|---|---|
| `config.repo` | yes | Repository in `owner/repo` format. |
| `config.head_commit_sha` | yes | Head commit SHA for the PR. |
| `config.token` | yes | GitHub token, resolved by `token-resolver`. |
| `config.required_checks` | no | List of required check names. |

## Operations

### `fetch_check_runs(pr_id, head_commit_sha)`

Output:

```yaml
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
```

### `fetch_job_log_summary(failing_check)`

Output:

```yaml
summary: "Error: expected 200 but got 401 at src/auth/login.test.ts:42"
full_log_url: https://github.com/owner/repo/actions/runs/123/logs
error_lines:
  - "FAIL src/auth/login.test.ts:42"
  - "Expected: 200"
  - "Received: 401"
```

## Output envelope

The adapter returns the standard `pr-adapter-contract` envelope with `Findings` containing the `ci-source` data.

## Status values

| Status | Meaning |
|---|---|
| `complete` | All check runs fetched and normalized. |
| `partial` | Some data unavailable. |
| `needs_input` | Token missing or invalid. |
| `blocked` | Repository or commit unreachable. |
| `skipped` | Not applicable. |

## Rules

- Return normalized `ci-source` shape, not raw API responses.
- Never log or expose the token.
- Mark `is_required` only for checks in `required_checks`.
- Keep `error_lines` short and relevant.
