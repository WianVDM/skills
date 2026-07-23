# Dependencies

## Required skills

- `detect-project-context` — project root and directory detection.
- `initialize-skill` — first-run config loading, intake, and persistence.
- `context-reports` — shared context report conventions.
- `worker-contract` — canonical worker return format.
- `identity-resolver` — work-item identity resolution.
- `tool-discovery` — model-first tool detection, capability resolution, and the per-project recipe cache.
- `artifact-freshness` — checks whether prior reports are safe to reuse.
- `chainlog` — stores per-capability observations (opt-in per run).
- `git-worktree-inspector` — safe local checkout without switching the user's branch.
- `scope-checker` — challenges proposed findings against ticket scope.
- `pr-adapter-contract` — the normalized shapes tool output is mapped to at fetch time.
- `checkpoint` — phase checklists and resume state.
- `scan-context` — discovery of prior context reports.
- `token-resolver` — secure token resolution when a resolved recipe needs one.

## Recommended skills

- `post-github-pr-review` — posting for GitHub PRs. Without it (or on non-GitHub platforms), the skill hands back the exact manual payload.

## Optional skills

- `debrief` — richer ticket scope.
- `baseline` — pre-change UI or system-state evidence.
- `research-ticket` — deeper ticket context when needed.

## Deprecated dependencies

The provider-specific adapter skills (`github-pr-adapter`, `github-actions-adapter`, `jira-adapter`, `sonarcloud-adapter`, `manual-pr-adapter`) are no longer used. Capabilities are resolved generically: `tool-discovery` finds and validates a working tool per capability, and output is mapped to the `pr-adapter-contract` shape at fetch time. See Phase 0 decision 1 in the 2026-07-20 audit.

## Required environment

- `git` — local branch checkout and inspection.
- Python 3.x — for running scripts.

## Environment variables

No secrets are hardcoded. Tokens are referenced by name and resolved via `token-resolver`. Common variables:

- `GITHUB_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN`
- `GITLAB_TOKEN`
- `JIRA_TOKEN` / `JIRA_API_TOKEN`
- `SONAR_TOKEN` / `SONARCLOUD_TOKEN`
