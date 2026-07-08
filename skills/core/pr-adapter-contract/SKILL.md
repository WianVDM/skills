---
name: pr-adapter-contract
description: Defines the normalized adapter interface contract for the pr-report conductor. Use when authoring or reviewing a pr-report adapter, implementing the adapter envelope, or mapping a new PR platform, CI system, static-analysis tool, issue tracker, or notification source into the pr-report shape.
license: Proprietary
invocation: model-invoked
metadata:
  tags: [pr-report, adapter, contract, building-block]
  author: Wian van der Merwe
  version: "1.0.1"
---

# PR Adapter Contract

Building block that defines the normalized interface between the `pr-report` conductor and its adapters. Adapters translate provider-specific data into these shapes; the conductor owns synthesis and reporting.

## Skill type

Building block. Reusable reference for adapter authors and the conductor.

## In scope

- Define the normalized adapter envelope and its five status values.
- Specify the operations and output shapes for each adapter role.
- State the rules every adapter must follow.

## Out of scope

- Synthesizing or triaging issues. The conductor owns that.
- Writing the PR report. The conductor owns that.
- Fixing code or replying to comments. The entire skill is out of scope for that.
- Provider-specific implementation details. Each adapter owns those.

## Adapter roles

| Role | Provides | Examples |
|---|---|---|
| `pr-source` | PR metadata, changed files, reviews, inline threads | GitHub, GitLab, Gitea, Azure DevOps, Bitbucket, Manual |
| `ci-source` | Check/pipeline status and failing logs | GitHub Actions, Azure Pipelines, GitLab CI, Jenkins |
| `static-analysis-source` | Code-quality findings | SonarQube, SonarCloud, CodeQL, Semgrep, Codacy |
| `issue-tracker-source` | Ticket scope, acceptance criteria | Jira, Linear, GitHub Issues, Azure Boards |
| `notification-source` | Feedback from chat/email/meeting tools | Teams, Slack, email, meeting notes |
| `context-report-source` | Pre-existing `.agents/context/` reports | Any skill report |

## Adapter envelope

Every adapter returns a result envelope:

```yaml
---
status: complete | partial | needs_input | blocked | skipped
source_type: github | gitlab | gitea | azure-devops | manual | teams | csv | ...
adapter: github-pr-adapter
confidence: high | medium | low
---

## Summary
Brief statement of what the adapter found or why it failed.

## Findings
The normalized data for this source type.

## Decisions made
- Source selected because config said `adapters.pr.source: github-pr-adapter`.
- Token resolved from `GITHUB_TOKEN` environment variable.

## Open questions
- ...

## Blockers
- ...
```

### Status semantics

| Status | Meaning | Conductor behavior |
|---|---|---|
| `complete` | Data fetched successfully. | Use the data. |
| `partial` | Some data fetched, but not all. | Use what is available and note gaps. |
| `needs_input` | The adapter needs a token, URL, or file from the user. | Ask the user and retry. |
| `blocked` | A configured adapter failed to connect. | Stop and consult the user. |
| `skipped` | The adapter is missing or disabled. | Continue without that source. |

## Interface operations

### PR source

- `resolve_pr(user_input, repo, current_branch)` → `pr_number`, `repo`, `branch`, `base`, `ticket_key`, `url`
- `fetch_metadata(pr_id)` → title, body, author, state, draft, base, head, mergeable, review decision
- `fetch_changed_files(pr_id)` → list of files with status, additions, deletions, previous path
- `fetch_reviews(pr_id)` → list of reviews with id, reviewer, state, body, submitted_at
- `fetch_review_threads(pr_id)` → list of threads with path, line, is_resolved, resolution, source_type, comments

### CI / build

- `fetch_check_runs(pr_id, head_commit_sha)` → status, checks with name, status, conclusion, url, is_required, summary
- `fetch_job_log_summary(failing_check)` → summary, full_log_url, error_lines

### Static analysis

- `fetch_findings(pr_id, project_key)` → findings with key, rule, severity, message, path, line, status, url, source_type

### Issue tracker / scope

- `resolve_ticket(key, repo, pr_title, pr_body)` → ticket_id, key, url
- `fetch_scope(ticket_id)` → key, title, body, acceptance_criteria, status, url

### Notification / comment

- `fetch_feedback(pr_id, ticket_key, config)` → comments with id, author, body, created_at, source_type, channel, severity, file, line, url

### Context report

- `discover_reports(key, pr_number, repo, branch)` → reports with path, skill, relevance, summary

## Adapter rules

- Return the normalized shape, not raw provider data.
- Never log or expose the resolved token.
- If the token is missing or invalid, return `needs_input` with the required env-var name.
- If the provider is unreachable, return `blocked` with the error detail.
- If only partial data is available, return `partial` and note what is missing.
- Mark required checks explicitly using `is_required`.

## References

- `pr-report` skill — the conductor that consumes this contract
- `worker-contract` skill — return contract format
- `token-resolver` skill — token resolution order
- `context-reports` skill — shared context-report conventions
