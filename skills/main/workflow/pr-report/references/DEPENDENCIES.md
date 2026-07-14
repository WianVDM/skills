# Dependencies

## Required skills

- `detect-project-context` — locates the project root, config directory, and context directory.
- `context-reports` — provides the canonical vocabulary and conventions for context reports.
- `worker-contract` — provides the canonical subagent return contract.
- `token-resolver` — resolves tokens from env vars, MCP config, or user input without leaking secrets.

## Internal subagents

The following workers are defined inside `pr-report/subagents/` and are not separate skills:

- `checkpoint-manager` — maintains phase checklist and resume state.
- `context-scout` — scans context reports for related ticket/issue keys.
- `issue-synthesizer` — groups, challenges, and weights feedback into an actionable issue board.
- `scope-checker` — compares feedback against ticket scope or PR intent.
- `report-writer` — fills pending report sections.
- `html-renderer` — renders the optional HTML dashboard.
- `normalize-pr` — normalizes PR metadata, changed files, reviews, and threads.
- `normalize-ci` — normalizes check runs and log summaries.
- `normalize-static-analysis` — normalizes code-quality findings.
- `normalize-issue-tracker` — normalizes ticket scope and acceptance criteria.

## Tool providers

The conductor discovers the best available tool for each capability. Out-of-box providers include:

- **PR source** — GitHub (via MCP or `gh` CLI), manual fallback.
- **CI / build** — GitHub Actions (via MCP or `gh` CLI).
- **Static analysis** — SonarCloud (via MCP or API).
- **Issue tracker** — Jira (via MCP or API).

Community or future providers (GitLab, Bitbucket, Azure DevOps, SonarQube, CodeQL, Semgrep, Linear, GitHub Issues) may be added as direct tools or separate skills when they are needed by more than one consumer.

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
- Access to at least one PR source tool (GitHub MCP/`gh`, or manual input).
- Optional access to CI, static-analysis, and issue-tracker tools depending on configuration.

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
