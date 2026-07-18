---
name: sonarcloud-adapter
description: Static-analysis source adapter that fetches SonarCloud findings and returns the normalized static-analysis shape.
invocation: model-invoked
depends:
  - pr-adapter-contract
  - worker-contract
  - token-resolver
---

# sonarcloud-adapter

Tool building block that implements the `static-analysis-source` adapter interface. It translates SonarCloud issue data into the normalized static-analysis shape.

## Skill type

Tool building block.

## When to use

- The configured static-analysis source is SonarCloud.
- The project has a SonarCloud project configured.

## In scope

- Fetch SonarCloud issues for a configured project key and organization.
- Filter findings by pull request or branch when provided.
- Map SonarCloud severity and issue states to the normalized `static-analysis-source` shape.
- Return the adapter envelope status and confidence.

## Out of scope

- Synthesizing, triaging, or auto-fixing findings.
- Writing the PR report.
- Running new SonarCloud analyses or mutating project configuration.
- Handling SonarQube Server-specific APIs directly.
- Resolving tokens directly.

## Inputs

```yaml
config:
  organization: my-org
  project_key: my-org_repo
  token: ${SONAR_TOKEN}
  branch: feature/OC-1234-fix
```

## Outputs

Standard worker return contract with the `static-analysis-source` adapter shape.

## Interface operations

- `fetch_findings(pr_id, project_key)` → normalized `{ findings }`.

## Completion criteria

- `complete`: SonarCloud issues fetched and normalized for the project/branch.
- `partial`: Some issues unavailable; missing items listed.
- `needs_input`: Token missing or invalid, or project key missing.
- `blocked`: Project key or organization invalid, or API unreachable.
- `skipped`: Not applicable.

## Rules

- Return the normalized `static-analysis-source` shape, not raw SonarCloud API responses.
- Never log or expose the resolved token.
- Map `source_type` to `static_analysis` for every finding.
- Include the SonarCloud issue URL when available.
- Distinguish `complete`, `partial`, `needs_input`, `blocked`, and `skipped` clearly.

## Provider limitations

SonarCloud behaviors that produce false negatives if unhandled:

- **PR analyses are not branches.** Querying issues by `branch` for a pull request analysis is inconclusive. Query with `pullRequest=<n>` instead. An empty branch-query result does not mean zero findings.
- **Project keys are case-sensitive and fail silently.** A wrong-cased `project_key` returns an empty result with no error. Verify the key casing (for example, against the SonarCloud project URL) before trusting an empty result.
- **A passed Quality Gate can still carry new issues.** Gate conditions may not block on lower-severity findings. Never use gate status as a proxy for findings; always fetch the findings themselves.
- **Empty result handling.** An empty result where the analysis's existence is unverified is inconclusive: return `partial` with `low` confidence and an explanatory note — never `complete` with zero findings. If the project key itself is unverified, return `blocked`.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Dependencies](references/DEPENDENCIES.md)
- [Interface](references/INTERFACE.md)
- `pr-adapter-contract` — adapter interface contract
- `worker-contract` — return contract format
- `token-resolver` — token resolution
