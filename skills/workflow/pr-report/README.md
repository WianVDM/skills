# pr-report

Build an actionable understanding of a pull request.

## Purpose

This skill gathers PR metadata, review feedback, inline comments, CI/build status, and static-analysis findings. It normalizes all feedback into a concise issue board where every comment is challenged against ticket scope and actual changes. The output is a structured report and an optional HTML dashboard.

## When to use

- Check PR status and review feedback.
- Triage PR comments from humans, bots, and hybrid reviewers.
- Understand CI/build failures and static-analysis findings.
- See what changed since the last check on a PR.

## Directory layout

```
pr-report/
├── SKILL.md                        # main skill instructions
├── README.md                       # this file
├── config.yaml                     # skill-specific config declaration
├── references/
│   ├── ADAPTER_ARCHITECTURE.md     # adapter taxonomy and discovery model
│   ├── ADAPTER_REGISTRY.md         # default adapter registry
│   ├── REFERENCE.md                # state spec, report schema, delta rules
│   ├── CONFIG_PATTERN.md           # config + notes pattern
│   ├── CAPABILITIES.md             # adapter discovery and capability detection
│   ├── CONTEXT_REPORTS.md          # output schemas
│   ├── DEPENDENCIES.md             # consumed context and required capabilities
│   ├── WORKFLOW.md                 # detailed step sequence
│   ├── COMMENT_TRIAGE.md           # source weighting and challenge rules
│   ├── CHECKPOINTING.md            # incremental output + resume rules
│   ├── EXAMPLES.md                 # example reports and states
│   ├── VALIDATION.md               # review checklist
│   └── VERSIONING.md               # skill and schema version policy
├── subagents/
│   ├── scope-checker.md            # compare feedback to ticket scope
│   ├── issue-synthesizer.md        # group, challenge, weight, decide
│   ├── report-writer.md            # compile final markdown report
│   ├── html-renderer.md            # optional HTML dashboard
│   ├── checkpoint-manager.md       # maintain phase checklist and resume state
│   └── context-scout.md            # scan context for related reports
└── assets/
    └── templates/
        └── report-dashboard.html   # optional HTML dashboard template
```

## Key conventions

- Config and notes live in the detected project config directory (default `{project-root}/.agents/config/pr-report.yaml`).
- Reports and state live in the detected project context directory (default `{project-root}/.agents/context/pr-report/`).
- All data sources are provided by pluggable adapter building blocks. The skill only orchestrates and synthesizes.
- The built-in PR source adapter is `github-pr-adapter`; the fallback is `manual-pr-adapter`.
- Optional adapters (CI, static-analysis, issue-tracker, notification) are lazy-loaded only when configured or detected.
- The skill scans the project context directory for any reports related to the ticket/issue key.
- The report is written incrementally to survive context compaction.
- The checkpoint manager maintains phase checklist and resume state.
- All comments are tracked in state; only actionable issues surface in the chat summary.
- The skill does not recommend next skills.

## Adapter skills

The redesigned `pr-report` consumes adapter building blocks and shared skills:

- `github-pr-adapter` — PR metadata, files, reviews, threads from GitHub.
- `github-actions-adapter` — CI check runs and logs from GitHub Actions.
- `sonarcloud-adapter` — static-analysis findings from SonarCloud.
- `jira-adapter` — ticket scope and acceptance criteria from Jira.
- `manual-pr-adapter` — fallback for unsupported tools or manual processes.
- `pr-adapter-contract` — normalized adapter interface contract.
- `token-resolver` — shared token resolution from env vars, MCP config, or user input.
- `worker-contract` — canonical worker return format.
- `context-reports` — shared context report conventions.

Community and custom adapters can be added to the adapter registry without changing the core skill.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on intent and move detailed guidance into `references/`. Preserve existing user preferences by pre-populating first-run questions with previous defaults. Prefer updating adapter skills over changing the conductor when the change is provider-specific.
