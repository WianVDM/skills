# Reference

PR report state management, internal normalization model, delta computation, and report generation for `pr-report`.

## Configuration

See [CONFIG_PATTERN.md](CONFIG_PATTERN.md) for the full config schema and token-resolution rules.

## Resolve PR

Try in order until one succeeds:

1. **Explicit number** — if the user provided digits, use as PR number.
2. **Ticket key** — if input matches `[A-Z][A-Z0-9_]+-\d+`, search open PRs for one whose title or branch contains the key. If multiple match, ask the user.
3. **Current branch** — detect the current branch and search for a PR whose head matches it.
4. **Ask** — ask the user for a PR number or URL.

Detect `owner/repo` from the git remote unless the user overrides it.

## PR resolution ambiguity rules

- **Multiple PRs matching a ticket key** — ask the user to pick one, or use the most recently updated one if confidence is medium.
- **No open PR for the current branch** — stop and ask the user to create a PR or provide a number.
- **PR URL provided** — parse `owner/repo/pull/number` from the URL and use it directly.
- **Forks** — detect the base repo from the upstream remote or the PR head repo from the PR URL.
- **Ambiguous repo** — if `git remote` has multiple entries, ask the user to select one and persist the choice.

## State file

Path: `{context_dir}/pr-report/{key}/state.md`

Frontmatter: `skill`, `version`, `key`, `pr_number`, `repo`, `branch`, `base`, `report_status`, `updated_at`, `commit_hash`.

Sections: Phase Checklist, Current Focus, Last Completed Action, PR Info, Detected Tools, Session History, Reviews Tracked, Comment History, Static Analysis Findings, CI / Build Status, Triage Decisions, Scope Flags, Files Changed.

Rules:

- Session History is append-only.
- Comment History appends a new row on every status change; do not delete old rows.
- Detected Tools records the preferred tool and ranking per capability.
- Status values: `open`, `resolved`, `uncertain`, `outdated`, `addressed-pending-resolve`, `dismissed-with-reason`, `no-action-needed`.
- Confidence values: `high`, `medium`, `low`.
- Update `Last Seen` on every iteration for findings and checks.

## Internal normalization model

All tool output is normalized into a common internal model before triage. The model is an internal schema, not a shared skill contract.

### Envelope

Every normalized capability result has:

```yaml
capability: string        # e.g., pr_metadata, ci, static_analysis, issue_tracker
status: complete | partial | missing | degraded
tool: string             # the tool that produced the data, e.g., github_mcp, gh_cli, sonarcloud_api
source: string           # provider name, e.g., github, github-actions, sonarcloud, jira
confidence: high | medium | low
findings: []             # list of normalized findings
errors: []               # list of errors, warnings, or degradation notes
better_tool: string | null  # name of a better tool that was available but unused
```

### Normalized findings

| Capability | Findings shape |
|---|---|
| PR metadata | `title`, `body`, `author`, `state`, `url`, `base_branch`, `head_branch`, `draft`, `created_at`, `updated_at` |
| Changed files | `path`, `status` (added/removed/modified), `patch` (optional), `previous_path` |
| Reviews | `id`, `author`, `body`, `state` (APPROVED/CHANGES_REQUESTED/COMMENTED), `submitted_at` |
| Threads / comments | `id`, `thread_id`, `author`, `body`, `path`, `line`, `created_at`, `status` |
| CI / build | `name`, `conclusion` (success/failure/skipped/neutral), `required`, `url`, `log_summary` |
| Static analysis | `rule`, `message`, `severity`, `path`, `line`, `effort`, `status` |
| Issue tracker scope | `key`, `title`, `description`, `acceptance_criteria`, `status`, `linked_prs` |

Missing or partial fields are handled gracefully. The `confidence` reflects the quality of the mapping.

## Delta computation

| Previous State | Fresh Fetch | Delta Classification |
|---|---|---|
| Not seen | Open | **New** |
| Open | Resolved | **Resolved since last check** |
| Open | Still open | **Still open** |
| Open | Uncertain | **Unclear status** |
| Our response "Resolved. ..." | Still open | **Addressed by us — pending resolve** |
| Open | Gone / outdated | **Outdated** |
| Passing | Failing | **New failure** |
| Failing | Passing | **Fixed** |

## Scope-source fallback hierarchy

`scope-checker` uses scope sources in this order:

1. `debrief` report for the ticket (if fresh).
2. Issue tracker ticket (title, description, acceptance criteria).
3. PR description / linked issues.
4. PR title and branch name.
5. User confirmation (if scope is still unclear).

If the scope source is stale or missing, the conductor notes the limitation and downgrades the confidence of scope-drift flags.

## Report template

The report template schema is documented in [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md). This section covers the state and delta logic only.

The report uses the following sections and status markers:

- Sections: PR Summary, Changed Files, CI / Build Status, Static Analysis Findings, Issues Requiring Action, Resolved Since Last Check, Threads with Unclear Status, Addressed by Us — Pending Resolve, Rebuttals Requiring Response, Reviewer Status, Scope Flags, Dismissed / No Action Needed, Data Sources, Task List.
- Mark each section with `<!-- STATUS: pending -->` initially and `<!-- STATUS: completed -->` when filled.

## Chat delivery

After generating the report, deliver a concise summary including:

- PR number and iteration
- Open items needing action
- Top 3–5 issues by severity and source
- Resolved since last check
- Review state and CI/build status
- Generated task list
- Suggested next step
- Link to the full report

If nothing changed, say so and repeat the current state.

## Versioning and migration

See [VERSIONING.md](VERSIONING.md).
