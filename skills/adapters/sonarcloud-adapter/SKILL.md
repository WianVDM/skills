---
name: sonarcloud-adapter
description: Static-analysis source adapter for the pr-report conductor. Fetches SonarCloud findings and returns the normalized static-analysis shape.
invocation: model-invoked
metadata:
  tags: [pr-report, adapter, static-analysis-source, sonarcloud, building-block]
  author: Wian van der Merwe
  version: "1.0.1"
---

# sonarcloud-adapter

Tool building block that implements the `static-analysis-source` adapter interface for the redesigned `pr-report` skill. It translates SonarCloud issue data into the normalized static-analysis shape expected by the conductor.

## In scope

- Fetch SonarCloud issues for a configured project key and organization.
- Filter findings by pull request or branch when provided.
- Map SonarCloud severity and issue states to the normalized `static-analysis-source` shape.
- Return the adapter envelope status (`complete`, `partial`, `needs_input`, `blocked`, `skipped`) and confidence.
- Accept configuration provided by `pr-report` (`organization`, `project_key`, `token`, `branch`, `pull_request`, etc.).

## Out of scope

- Synthesizing, triaging, or auto-fixing findings. The conductor owns that.
- Writing the PR report. The conductor owns that.
- Running new SonarCloud analyses or mutating project configuration.
- Handling SonarQube Server-specific APIs directly (use `sonarqube-adapter` or a generic HTTP adapter).
- Resolving tokens directly. The shared `token-resolver` building block resolves `SONAR_TOKEN`, `SONARQUBE_TOKEN`, or `SONARCLOUD_TOKEN`.

## When to use

Use this adapter when the `pr-report` configuration selects it as the static-analysis source:

```yaml
adapters:
  static_analysis:
    source: sonarcloud-adapter
    config:
      organization: my-org
      project_key: my-org_repo
      token: ${SONAR_TOKEN}
```

## Interface operations

Implements the `static-analysis-source` interface from `pr-adapter-contract`:

- `fetch_findings(pr_id, project_key)` → normalized `{ findings }`

## Example input

```yaml
config:
  organization: my-org
  project_key: my-org_repo
  token: ${SONAR_TOKEN}
  branch: feature/OC-1234-fix
```

## Example output (worker return contract)

```yaml
---
status: complete
artifacts: []
---

## Summary
Fetched 2 SonarCloud issues for my-org_repo on branch feature/OC-1234-fix.

## Findings
adapter_role: static-analysis-source
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

## Decisions made
- Source selected because pr-report config set `static_analysis.source: sonarcloud-adapter`.
- Token resolved via the token-resolver building block from `SONAR_TOKEN`.
- SonarCloud severity `BLOCKER` and `CRITICAL` map to `blocker`/`critical`, `MAJOR` to `major`, `MINOR` to `minor`, `INFO` to `info`.

## Open questions
- None.

## Blockers
- None.
```

## Rules

- Return the normalized `static-analysis-source` shape, not raw SonarCloud API responses.
- Never log or expose the resolved token.
- Distinguish `complete`, `partial`, `needs_input`, `blocked`, and `skipped` clearly.
- If the token is missing or invalid, return `needs_input` with the required env-var name.
- If the project key or organization is invalid, return `blocked` with the error detail.
- If the API is partially reachable, return `partial` and note which findings could not be fetched.
- Map `source_type` to `static_analysis` for every finding.
- Include the SonarCloud issue URL when available so the conductor can link directly to it.
- Reference the adapter contract at `pr-adapter-contract` for envelope shape and status semantics.

## References

- `pr-adapter-contract` skill — adapter interface contract
- `pr-report/references/ADAPTER_ARCHITECTURE.md` — high-level adapter architecture
- `worker-contract` skill — return contract format
- `token-resolver` building block — token resolution
