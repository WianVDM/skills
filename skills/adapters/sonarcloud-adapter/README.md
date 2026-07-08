# sonarcloud-adapter

Static-analysis source adapter for `pr-report`.

## Purpose

Fetch SonarCloud findings for a project and return the normalized `static-analysis-source` shape.

## When to use

When `pr-report` config points `adapters.static_analysis.source` to `sonarcloud-adapter` and the project is hosted on SonarCloud.

## Inputs

| Field | Description |
|---|---|
| `organization` | SonarCloud organization key. |
| `project_key` | SonarCloud project key. |
| `token` | Resolved SonarCloud token (via `token-resolver`). |
| `branch` | Optional branch to scope findings. |
| `pull_request` | Optional pull request identifier to scope findings. |

## Outputs

Normalized `static-analysis-source` data:

- `findings`: array of findings with key, rule, severity, message, path, line, status, URL, and `source_type: static_analysis`.

See `SKILL.md` for the full interface and worker-return-contract example.
