# Dependencies

## Required skills

- `detect-project-context` — locates the project root, config directory, and context directory.
- `context-reports` — provides the canonical vocabulary and conventions for context reports.
- `worker-contract` — provides the canonical subagent return contract.
- `token-resolver` — resolves tokens from env vars, MCP config, or user input without leaking secrets.
- `pr-adapter-contract` — defines the normalized adapter interface contract.

## Internal subagents

The following workers are defined inside `pr-report/subagents/` and are not separate skills:

- `checkpoint-manager` — maintains phase checklist and resume state.
- `context-scout` — scans context reports for related ticket/issue keys.
- `issue-synthesizer` — groups, challenges, and weights feedback into an actionable issue board.
- `scope-checker` — compares feedback against ticket scope or PR intent.
- `report-writer` — fills pending report sections.
- `html-renderer` — renders the optional HTML dashboard.

## Adapter skills

The conductor invokes adapter building blocks by name. At least one PR source adapter is required. All others are optional and loaded lazily.

### Built-in adapters

- `github-pr-adapter` — PR metadata, files, reviews, and inline threads from GitHub.
- `github-actions-adapter` — CI check runs and logs from GitHub Actions.
- `sonarcloud-adapter` — static-analysis findings from SonarCloud.
- `jira-adapter` — ticket scope and acceptance criteria from Jira.
- `manual-pr-adapter` — fallback for unsupported tools or manual processes.
- `context-report-adapter` — discovers related reports in the context directory.

### Community / optional adapters

- `gitlab-pr-adapter`, `gitlab-ci-adapter`
- `gitea-pr-adapter`
- `azure-devops-pr-adapter`, `azure-pipelines-adapter`
- `bitbucket-pr-adapter`
- `sonarqube-adapter`, `codeql-adapter`, `semgrep-adapter`
- `linear-adapter`, `github-issues-adapter`
- `teams-adapter`, `slack-adapter`

See `references/ADAPTER_ARCHITECTURE.md` for the adapter interface and registry format.

## Consumed context reports

The skill scans `{context_dir}/` for reports matching the ticket or PR key. Relevant reports include, but are not limited to:

- `{context_dir}/debrief/{key}.md` — ticket scope, acceptance criteria, assumptions.
- `{context_dir}/baseline/{key}.md` — UI evidence or pre-change state.
- Any `{context_dir}/{type}/{key}.md` report whose frontmatter references the ticket or PR.

Any matching report type may be consumed if it adds useful context. The skill handles absence gracefully.

## Required tools and capabilities

- Read files in the project.
- Write files to the detected context directory.
- Execute scripts (Python 3.x) for deterministic helpers.
- Access to the configured PR source adapter (GitHub, GitLab, Gitea, Azure DevOps, Bitbucket, or manual input).
- Optional access to CI, static-analysis, issue-tracker, and notification adapters depending on configuration.

## Environment variables

No environment variables are hardcoded. Token references are resolved through the `token-resolver` building block. Commonly referenced variables include:

- `GITHUB_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN`
- `GITLAB_TOKEN`
- `SONAR_TOKEN` / `SONARQUBE_TOKEN` / `SONARCLOUD_TOKEN`
- `JIRA_TOKEN` / `JIRA_API_TOKEN`

The skill references these only by name in config; it never writes secret values to report or state files.

## Optional enhancements

Other skills may produce useful context reports, but none are required:

- `debrief` — produces ticket-scope context.
- `baseline` — produces pre-change UI or system-state evidence.

These are treated as optional enhancements, not dependencies.
