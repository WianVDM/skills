# Dependencies

## Required skills

- `detect-project-context` — project root and directory detection.
- `initialize-skill` — first-run config loading and creation.
- `context-reports` — shared context report conventions.
- `worker-contract` — canonical worker return format.
- `token-resolver` — secure token resolution.
- `identity-resolver` — work-item identity resolution.
- `tool-discovery` — discovers and ranks available tools.
- `artifact-freshness` — checks whether prior reports are safe to reuse.
- `chainlog` — stores per-capability tool output.
- `git-worktree-inspector` — safe local checkout without switching the user's branch.
- `scope-checker` — challenges proposed comments against scope.
- `pr-adapter-contract` — normalized adapter interface.

## Recommended skills

- `verify-branch` — for running targeted checks when configured appropriately.
- `github-pr-adapter` — GitHub PR source adapter.
- `github-actions-adapter` — GitHub Actions CI adapter.
- `jira-adapter` — Jira issue-tracker adapter.
- `sonarcloud-adapter` — SonarCloud static-analysis adapter.
- `manual-pr-adapter` — Manual PR source adapter.
- `post-github-pr-review` — GitHub PR review posting tool.

## Optional skills

- `debrief` — for richer ticket scope.
- `baseline` — for pre-change UI or system-state evidence.
- `research-ticket` — for deeper ticket context when needed.

## Required environment

- `git` — local branch checkout and inspection.
- Python 3.x — for running scripts.

## Environment variables

No secrets are hardcoded. Tokens are referenced by name and resolved via `token-resolver`. Common variables:

- `GITHUB_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN`
- `JIRA_TOKEN` / `JIRA_API_TOKEN`
- `SONAR_TOKEN` / `SONARCLOUD_TOKEN`
