# Reports and Context

`pr-report` produces project-level reports and consumes context from other skills when available.

## Produced reports

### Markdown report

```text
{context_dir}/pr-report/{key}-report.md
```

Canonical report. Contains PR summary, changed files, CI status, static analysis, triaged issues, resolved items, unclear items, scope flags, and a **Data sources** section listing the tool used for each capability.

### HTML dashboard

```text
{context_dir}/pr-report/{key}-report.html
```

Optional human-facing dashboard rendered from the Markdown report. The Markdown report remains canonical.

### State file

```text
{context_dir}/pr-report/{key}/state.md
```

Working memory: phase checklist, comment history, review tracking, CI history, triage decisions.

`{context_dir}` is discovered by `detect-project-context`. The default is `{project-root}/.agents/context`, but the skill does not assume that path.

## Key placeholder

`{key}` is derived as:

1. Ticket key extracted from PR title, branch, or body (regex `[A-Z][A-Z0-9_]+-\d+`).
2. If no ticket key, use `pr-{pr_number}`.

## Consumed context

The skill scans `{context_dir}/` for reports that relate to the current PR or ticket. It does not assume that any specific report type exists.

### Scanning behavior

1. Derive `{key}` from the PR (ticket key if available, otherwise `pr-{pr_number}`).
2. Walk `{context_dir}/` recursively.
3. Consider any file whose basename contains `{key}` a candidate report.
4. Read the frontmatter of each candidate.

### Relevance from frontmatter

A candidate report is treated as relevant when its frontmatter contains any of the following:

- `ticket: {key}`
- `key: {key}`
- `pr_number: {pr_number}`
- `repo: {owner/repo}`
- `branch: {branch}`

The skill also treats reports as relevant when their `summary`, `description`, or `artifacts` fields mention the PR number, branch, or ticket key.

### Using scanned context

- Scope checking uses relevant reports to understand ticket intent, acceptance criteria, assumptions, and baseline evidence.
- The most specific report (for example, one whose `ticket` matches exactly) takes precedence over loosely matched reports.
- Relevant reports are listed in the produced report's frontmatter `consumed_context` array so their influence is transparent.

### Fallback behavior

- If no related context is found, the skill falls back to the PR title, description, and linked issues for scope.
- If only loosely related context is found, the skill notes the match quality and uses it cautiously.
- The skill never fails because a specific report type is missing.

### Local config

`{config_dir}/pr-report.yaml` supplies adapter selection, tokens by reference, and bot mappings. It is read on every run.

## Data sources section

The canonical report must include a **Data sources** section (after the triaged sections and before finalization) that lists, for every capability, the tool that was used and any alternatives that were available: [rest stays same]

- Capability name (e.g., PR metadata, CI / build status, static analysis findings).
- Tool used (e.g., `github-pr-adapter`, GitHub MCP, `gh`).
- Alternative tools detected.
- Whether a degraded source was accepted, and if so, why and what better tool was available.
- Confidence assigned to the data from that source.

This section makes the tool-selection process transparent and auditable. It is generated during the collect phase and finalized before the report is presented.

## Report freshness

- The Markdown report is rewritten every iteration.
- The state file is updated incrementally.
- The HTML variant is regenerated from the Markdown report after finalization.
