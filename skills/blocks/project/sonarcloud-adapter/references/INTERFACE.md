# Interface

`sonarcloud-adapter` implements the `static-analysis-source` interface from `pr-adapter-contract`.

## Input

```yaml
config:
  organization: my-org
  project_key: my-org_repo
  token: ${SONAR_TOKEN}
  branch: feature/OC-1234-fix
```

| Field | Required | Description |
|---|---|---|
| `config.organization` | yes | SonarCloud organization. |
| `config.project_key` | yes | SonarCloud project key. |
| `config.token` | yes | SonarCloud token, resolved by `token-resolver`. |
| `config.branch` | no | Branch to filter findings. |
| `config.pull_request` | no | Pull request ID to filter findings. |

## Operations

### `fetch_findings(pr_id, project_key)`

Output:

```yaml
findings:
  - key: "AZYx1234"
    rule: "typescript:SUnusedVariable"
    severity: minor
    message: "Remove unused import."
    path: src/auth/login.ts
    line: 5
    status: open
    url: https://sonarcloud.io/project/issues?id=my-org_repo&open=AZYx1234
    source_type: static_analysis
  - key: "AZYx5678"
    rule: "typescript:S1523"
    severity: major
    message: "Make sure that this dynamic injection is safe."
    path: src/auth/login.ts
    line: 28
    status: false_positive
    url: https://sonarcloud.io/project/issues?id=my-org_repo&open=AZYx5678
    source_type: static_analysis
```

## Output envelope

The adapter returns the standard `pr-adapter-contract` envelope with `Findings` containing the `static-analysis-source` data.

## Status values

| Status | Meaning |
|---|---|
| `complete` | Issues fetched and normalized. |
| `partial` | Some issues unavailable. |
| `needs_input` | Token missing or invalid, or project key missing. |
| `blocked` | Project or organization invalid, or API unreachable. |
| `skipped` | Not applicable. |

## Rules

- Return normalized `static-analysis-source` shape, not raw API responses.
- Never log or expose the token.
- Map `source_type` to `static_analysis` for every finding.
- Include the SonarCloud issue URL when available.
