# Dependencies

The dependency taxonomy follows `docs/skill-standards/fundamentals/architecture/dependencies-and-bundling.md`: **required** (the skill cannot function without it), **recommended** (improves output; the skill runs degraded without it), **optional** (side branches or advanced features).

## Required skills

- `detect-project-context` — locates the project root, config directory, and context directory.
- `initialize-skill` — creates, migrates, and loads `{config_dir}/pr-report.yaml`.
- `identity-resolver` — resolves a PR number, ticket key, branch, or commit from user input.
- `tool-discovery` — discovers and ranks available tools for each capability.
- `pr-adapter-contract` — canonical normalized shapes and envelope that `normalize-observation` maps tool output into.
- `worker-contract` — canonical subagent return contract.
- `token-resolver` — resolves tokens from env vars, MCP config, or user input without leaking secrets.
- `scope-checker` — classifies findings as in-scope, out-of-scope, or ambiguous.
- `scan-context` — discovers related context reports by ticket key, branch, or type.
- `checkpoint` — owns the state file schema and phase checklist operations.
- `chainlog` — append-only observation store; `pr-report` is a producer and consumer (see [CHAINLOG.md](CHAINLOG.md)).
- `artifact-freshness` — judges whether prior observations and reports are fresh enough to reuse.
- `context-reports` — canonical vocabulary and envelope for the produced report.

## Recommended skills

Provider adapters. The conductor prefers the best available tool per capability, which may be an MCP server, CLI, or direct API; these adapters are the documented fallback recipes and normalized-shape producers for their providers.

- `github-pr-adapter` — PR source for GitHub.
- `github-actions-adapter` — CI source for GitHub Actions.
- `sonarcloud-adapter` — static-analysis source for SonarCloud.
- `jira-adapter` — issue-tracker source for Jira.
- `manual-pr-adapter` — manual PR source fallback.

Community or future providers (GitLab, Bitbucket, Azure DevOps, SonarQube Server, CodeQL, Semgrep, Linear, GitHub Issues) may be added as direct tools or separate skills when they are needed by more than one consumer.

## Optional skills

- `debrief` — produces ticket-scope context reports consumed as scope input.
- `baseline` — produces pre-change UI or system-state evidence.

## Internal workers

Defined inside `pr-report/subagents/`; not separate skills:

- `normalize-observation` — maps raw tool output into the `pr-adapter-contract` shapes.
- `issue-synthesizer` — groups, challenges, and weights feedback into an actionable issue board.
- `report-writer` — fills pending report sections.
- `html-renderer` — renders the optional HTML dashboard.

## Consumed context reports

The skill consumes reports matching the ticket or PR key, discovered via `scan-context`. Relevant reports include, but are not limited to:

- `{context_dir}/debrief/{key}.md` — ticket scope, acceptance criteria, assumptions.
- `{context_dir}/baseline/{key}.md` — UI evidence or pre-change state.
- Any `{context_dir}/{type}/{key}.md` report whose frontmatter references the ticket or PR.

Reports under the `pr-report` subdirectory are excluded to avoid circular self-reference. The skill handles absence gracefully.

## Required tools and capabilities

- Read files in the project.
- Write files to the detected context directory.
- Execute scripts (Python 3.x) for deterministic helpers.
- Access to at least one PR source tool (GitHub MCP/`gh`, or manual input).
- Optional access to CI, static-analysis, and issue-tracker tools depending on configuration.

## Environment variables

No environment variables are hardcoded. Token references are resolved through the `token-resolver` building block. Commonly referenced variables include:

- `GITHUB_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN`
- `GITLAB_TOKEN`
- `SONAR_TOKEN` / `SONARQUBE_TOKEN` / `SONARCLOUD_TOKEN`
- `JIRA_TOKEN` / `JIRA_API_TOKEN`

The skill references these only by name in config; it never writes secret values to report, state, or chainlog files.
