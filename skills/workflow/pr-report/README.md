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
├── references/
│   ├── REFERENCE.md                # state spec, report schema, checklists
│   ├── CONFIG_PATTERN.md           # config + notes pattern
│   ├── CAPABILITIES.md             # available PR/CI/static-analysis sources
│   ├── CONTEXT_REPORTS.md          # output schemas
│   ├── DEPENDENCIES.md             # consumed context and required capabilities
│   ├── WORKFLOW.md                 # detailed step sequence
│   ├── PROVIDER_ADAPTERS.md        # PR platform adapter interface
│   ├── CI_ADAPTERS.md              # CI/build adapter interface
│   ├── STATIC_ANALYSIS.md          # static-analysis integration
│   ├── COMMENT_TRIAGE.md           # source weighting and challenge rules
│   ├── CHECKPOINTING.md            # incremental output + resume rules
│   ├── EXAMPLES.md                 # example reports and states
│   └── VALIDATION.md               # review checklist
├── subagents/
│   ├── pr-researcher.md            # resolve PR + fetch metadata/files/reviews
│   ├── thread-analyzer.md          # fetch + normalize review threads
│   ├── ci-status-fetcher.md        # fetch CI/build status and logs
│   ├── static-analysis-fetcher.md  # fetch static-analysis findings
│   ├── scope-checker.md            # compare feedback to ticket scope
│   ├── issue-synthesizer.md        # group, challenge, weight, decide
│   ├── report-writer.md            # compile final markdown report
│   ├── html-renderer.md            # optional HTML dashboard
│   ├── checkpoint-manager.md       # maintain phase checklist and resume state
│   └── context-scout.md            # scan .agents/context/ for related reports
├── scripts/
│   ├── detect-harness.py           # detect agent harness
│   ├── detect-mcp-config.py        # find MCP config files
│   ├── detect-pr-provider.py       # detect PR platform from git remote
│   ├── scan-related-context.py     # scan context for related reports
│   └── validate-token.py           # validate provider tokens
└── assets/
    └── templates/
        └── report-dashboard.html   # optional HTML dashboard template
```

## Key conventions

- Reports live in `.agents/context/pr-report/`.
- Config and notes live in `.agents/config/pr-report.yaml`.
- Multiple PR platforms, CI systems, and static-analysis tools are supported via adapter docs in `references/`.
- Provider and harness detection is the default; specific tools are configured only when needed.
- The skill scans `.agents/context/` for any reports related to the ticket/issue key.
- Detection and validation logic lives in deterministic scripts under `scripts/`.
- The report is written incrementally to survive context compaction.
- The checkpoint manager maintains phase checklist and resume state.
- All comments are tracked in state; only actionable issues surface in the chat summary.
- The skill does not recommend next skills.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on intent and move detailed guidance into `references/`. Preserve existing user preferences by pre-populating first-run questions with previous defaults.
