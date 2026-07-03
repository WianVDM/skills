# Dependencies

## Optional consumed context

The skill scans `.agents/context/` for any reports matching the ticket/issue key and uses relevant ones. Examples include:

- `.agents/context/debrief/{key}.md` — ticket scope, acceptance criteria, assumptions.
- `.agents/context/baseline/{key}.md` — UI evidence or pre-change state relevant to the PR.

Any matching report type may be consumed if it adds useful context. The skill handles absence gracefully.

## Required capabilities

- Access to the PR platform for the target repository (GitHub, Azure DevOps, GitLab, Bitbucket, or manual input).
- Optional access to CI/build systems, static-analysis services, and issue trackers depending on what is configured or detected.

## Environment variables

No environment variables are hardcoded. Tokens are resolved from config or detected MCP server config. Commonly referenced variables include:

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
