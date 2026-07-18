# Reference

PR report state management, normalization, delta computation, and report generation for `pr-report`.

## Configuration

See [CONFIG_PATTERN.md](CONFIG_PATTERN.md) for the full config schema and token-resolution rules.

## Resolve PR

Invoke `identity-resolver/scripts/resolve-identity.py` with the user input, repo hint, and branch hint. Use the returned envelope directly:

- `type: pr` → use `pr_number`, `repo`, `branch`, `base`, `commit`, `url`, `key`.
- `type: ticket` → use `key` as the ticket key; search open PRs for one whose title or branch contains the key. If multiple match, ask the user.
- `type: branch` → use `branch` and `repo`; search for a PR whose head matches the branch.
- `type: commit` → use `commit` and `repo`.

If `identity-resolver` returns `needs_input`, ask the user for a PR number or URL.

## PR resolution ambiguity rules

- **Multiple PRs matching a ticket key** — ask the user to pick one, or use the most recently updated one if confidence is medium.
- **No open PR for the current branch** — stop and ask the user to create a PR or provide a number.
- **PR URL provided** — parse `owner/repo/pull/number` from the URL and use it directly.
- **Forks** — detect the base repo from the upstream remote or the PR head repo from the PR URL.
- **Ambiguous repo** — if `git remote` has multiple entries, ask the user to select one and persist the choice.

## State file

Path: `{context_dir}/pr-report/{key}/state.md`

The state file follows the [`checkpoint`](../../../../blocks/project/checkpoint/SKILL.md) state schema: frontmatter (`skill`, `version`, `state_schema`, `owner`, `key`, `updated_at`) plus body sections Phase Checklist, Current Focus, Last Completed Action, and Session History. `owner` is `pr-report`.

`pr-report` adds frontmatter fields `pr_number`, `repo`, `branch`, `base`, `report_status`, `generated_at`, and `commit_hash`, and the following owner sections: PR Info, Detected Tools, Reviews Tracked, Comment History, Static Analysis Findings, CI / Build Status, Triage Decisions, Scope Flags, Files Changed.

Rules:

- Session History is append-only.
- Comment History appends a new row on every status change; do not delete old rows.
- Detected Tools records the preferred tool and ranking per capability.
- Status values: `open`, `resolved`, `uncertain`, `outdated`, `addressed-pending-resolve`, `dismissed-with-reason`, `no-action-needed`.
- Confidence values: `high`, `medium`, `low`.
- Update `Last Seen` on every iteration for findings and checks.

## Normalization

All tool output is normalized into the [`pr-adapter-contract`](../../../../blocks/project/pr-adapter-contract/SKILL.md) shapes before triage. The conductor delegates mapping to the `normalize-observation` worker; each capability uses the contract shape for its adapter role (`pr-source`, `ci-source`, `static-analysis-source`, `issue-tracker-source`).

### Envelope

The envelope uses the contract's status vocabulary with two `pr-report` extension fields:

```yaml
capability: string        # e.g., pr_metadata, ci_build, static_analysis, issue_tracker_scope
status: complete | partial | needs_input | blocked | skipped
tool: string              # extension: the tool that produced the data, e.g., github_mcp, gh_cli
source_type: string       # provider name, e.g., github, sonarcloud, jira
confidence: high | medium | low
findings: []              # normalized findings in the contract shape
errors: []                # errors, warnings, or degradation notes
better_tool: string | null  # extension: better tool that was available but unused
```

Status semantics follow the contract. An inconclusive result (silently empty, unverifiable) is reported as `partial` with `low` confidence — never `complete` with empty findings.

### Normalized findings

| Capability | Findings shape |
|---|---|
| PR metadata | `title`, `body`, `author`, `state`, `url`, `base_branch`, `head_branch`, `draft`, `created_at`, `updated_at` |
| Changed files | `path`, `status` (added/removed/modified), `patch` (optional), `previous_path` |
| Reviews | `id`, `author`, `body`, `state` (APPROVED/CHANGES_REQUESTED/COMMENTED), `submitted_at` |
| Threads / comments | `id`, `thread_id`, `author`, `body`, `path`, `line`, `created_at`, `status` |
| Conversation comments | `id`, `author`, `body`, `created_at`, `source_type`, `channel`, `url` |
| CI / build | `name`, `conclusion` (success/failure/skipped/neutral), `required`, `url`, `log_summary` |
| Static analysis | `rule`, `message`, `severity`, `path`, `line`, `effort`, `status` |
| Issue tracker scope | `key`, `title`, `description`, `acceptance_criteria`, `status`, `linked_prs` |

Missing or partial fields are handled gracefully. The `confidence` reflects the quality of the mapping. The canonical field definitions live in `pr-adapter-contract/references/INTERFACE.md`; the table above is a summary only.

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

The canonical report section list is the skeleton in [CHECKPOINTING.md](CHECKPOINTING.md); the full report schema is in [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md). Each section carries a `<!-- STATUS: pending -->` marker until filled.

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
