# Reference

PR report state management, delta computation, and report generation for `pr-report`.

## Configuration

See [CONFIG_PATTERN.md](CONFIG_PATTERN.md) for the full config schema and token-resolution rules.

## Resolve PR

Try in order until one succeeds:

1. **Explicit number** — if the user provided digits, use as PR number.
2. **Ticket key** — if input matches `[A-Z][A-Z0-9_]+-\d+`, search open PRs for one whose title or branch contains the key. If multiple match, ask the user.
3. **Current branch** — detect the current branch and search for a PR whose head matches it.
4. **Ask** — ask the user for a PR number or URL.

Detect `owner/repo` from the git remote unless the user overrides it.

## State file

Path: `{context_dir}/pr-report/{key}/state.md`

Frontmatter: `skill`, `version`, `key`, `pr_number`, `repo`, `branch`, `base`, `report_status`, `updated_at`.

Sections: Phase Checklist, Current Focus, Last Completed Action, PR Info, Session History, Reviews Tracked, Comment History, Static Analysis Findings, CI / Build Status, Triage Decisions, Scope Flags, Files Changed.

Rules:

- Session History is append-only.
- Comment History appends a new row on every status change; do not delete old rows.
- Status values: `open`, `resolved`, `uncertain`, `outdated`, `addressed-pending-resolve`, `dismissed-with-reason`, `no-action-needed`.
- Confidence values: `high`, `medium`, `low`.
- Update `Last Seen` on every iteration for findings and checks.

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

## Report template

Path: `{context_dir}/pr-report/{key}-report.md`.

Frontmatter: `skill`, `version`, `key`, `pr_number`, `repo`, `branch`, `base`, `report_status`, `updated_at`, `consumed_context`.

Sections: PR Summary, Changed Files, CI / Build Status, Static Analysis Findings, Issues Requiring Action, Resolved Since Last Check, Threads with Unclear Status, Addressed by Us — Pending Resolve, Rebuttals Requiring Response, Reviewer Status, Scope Flags, Dismissed / No Action Needed.

Mark each section with `<!-- STATUS: pending -->` initially and `<!-- STATUS: completed -->` when filled.

## Chat delivery

After generating the report, deliver a concise summary including:

- PR number and iteration
- Open items needing action
- Top 3–5 issues by severity and source
- Resolved since last check
- Review state and CI/build status
- Suggested next step
- Link to the full report

If nothing changed, say so and repeat the current state.

## Versioning and migration

See [VERSIONING.md](VERSIONING.md).
