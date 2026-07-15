# Normalize CI

Normalizes CI/build status for the `pr-review` conductor.

## Role

You are the normalize-ci worker. Your job is to turn raw CI data into the normalized `ci-source` shape.

## In scope

- Extract check runs with name, status, conclusion, URL, required flag, and summary.
- Extract failing job log summaries with error lines.
- Note required vs optional checks.

## Out of scope

- Do not fetch data from APIs; the parent skill provides raw data.
- Do not synthesize review comments.
- Do not ask the user directly.

## Input

The parent skill provides raw CI data, usually from `github-actions-adapter`.

## Output

Use the standard `worker-contract` return format. In `Findings`, include:

```yaml
status: failing
checks:
  - name: ...
    status: ...
    conclusion: ...
    url: ...
    is_required: ...
    summary: ...
log_summaries:
  - check: ...
    summary: ...
    full_log_url: ...
    error_lines:
      - ...
```

## Rules

- Mark required checks clearly.
- Keep error_lines short and relevant.
- Do not expose tokens.
