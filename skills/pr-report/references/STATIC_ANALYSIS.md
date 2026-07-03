# Static Analysis

The static-analysis adapter fetches findings from the configured provider for the PR. Findings are treated as `required` issues unless explicitly suppressed.

## Adapter interface

| Operation | Input | Output |
|-----------|-------|--------|
| `fetch_findings` | PR identifier, project key | list of findings with key, severity, message, file, line, status |

## Finding shape

```yaml
findings:
  - key: "AZYx1234"
    rule: "typescript:SUnusedVariable"
    severity: major
    message: "Remove unused import."
    path: src/auth/login.ts
    line: 5
    status: open
    url: https://sonarcloud.io/project/issues?id=...
```

## SonarCloud / SonarQube

Resolution order:

1. Direct SonarCloud/SonarQube API when token and project key are available.
2. SonarQube MCP server if installed.
3. Ask the user to paste findings or provide a token.
4. Skip / disable if the user chooses.

### On zero findings

A `total: 0` response is acceptable only if the call succeeded and you are confident the provider analyzed the PR. If the call failed or you are unsure, treat it as a connection failure and consult the user.

### Tracking

- Add each finding to the `## Static Analysis Findings` table.
- Update `Last Seen` on every iteration.
- If a finding disappears, mark it `resolved`.

## CodeRabbit

CodeRabbit comments are fetched through the PR adapter as review comments, not through the static-analysis adapter. They are categorized as `automated_reviewer` and triaged separately.

## Other providers (future)

- **CodeQL:** GitHub Advanced Security alerts.
- **Semgrep:** CI-published findings.
