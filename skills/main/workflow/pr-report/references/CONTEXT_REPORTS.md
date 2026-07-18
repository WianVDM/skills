# Reports and Context

`pr-report` produces project-level reports and consumes context from other skills when available.

## Produced reports

### Markdown report

```text
{context_dir}/pr-report/{key}-report.md
```

Canonical report. Contains PR summary, changed files, CI status, static analysis, triaged issues, resolved items, unclear items, scope flags, a generated task list, and a **Data sources** section listing the tool used for each capability.

The report frontmatter follows the `context-reports` envelope: `skill`, `version`, `key`, `generated_at` (ISO 8601, required), `summary`, plus `pr-report` fields (`pr_number`, `repo`, `branch`, `base`, `report_status`, `updated_at`) and `consumed_context`.

### HTML dashboard

```text
{context_dir}/pr-report/{key}-report.html
```

Optional human-facing dashboard rendered from the Markdown report. The Markdown report remains canonical.

### State file

```text
{context_dir}/pr-report/{key}/state.md
```

Working memory: phase checklist, comment history, review tracking, CI history, triage decisions. Frontmatter includes `generated_at` alongside the `checkpoint` schema fields and `pr-report` owner fields.

`{context_dir}` is discovered by `detect-project-context`. The default is `{project-root}/.agents/context`, but the skill does not assume that path.

## Key placeholder

`{key}` is derived as:

1. Ticket key extracted from PR title, branch, or body (regex `[A-Z][A-Z0-9_]+-\d+`).
2. If no ticket key, use `pr-{pr_number}`.

## Consumed context

Related reports are discovered with the `scan-context` block (matching, ranking, and freshness rules live there). Results whose `type` is `pr-report` (this skill's own subdirectory) are excluded to avoid circular self-reference.

### Using scanned context

- Scope checking uses relevant reports to understand ticket intent, acceptance criteria, assumptions, and baseline evidence.
- The most specific report (for example, one whose `ticket` matches exactly) takes precedence over loosely matched reports.
- Relevant reports are listed in the produced report's frontmatter `consumed_context` array so their influence is transparent.

### Fallback behavior

- If no related context is found, the skill falls back to the PR title, description, and linked issues for scope.
- If only loosely related context is found, the skill notes the match quality and uses it cautiously.
- The skill never fails because a specific report type is missing.

### Local config

`{config_dir}/pr-report.yaml` supplies tool provider selection, token references, and bot mappings. It is read on every run.

## Data sources section

The canonical report must include a **Data sources** section. The canonical specification is in [TOOL_SELECTION.md](TOOL_SELECTION.md#data-sources-section). It is generated during the collect phase and finalized before the report is presented.

## Report freshness

- The Markdown report is rewritten every iteration.
- The state file is updated incrementally.
- The HTML variant is regenerated from the Markdown report after finalization.
- The task list is regenerated from the issue board on every iteration.
