# pr-report

Build an actionable understanding of a pull request.

## What it does

`pr-report` is a capability-first conductor skill. For every load-bearing capability it needs — PR metadata, review feedback, inline comments, CI/build status, static-analysis findings, and ticket scope — it invokes `tool-discovery` to find the available tools, selects the best one, and falls back gracefully when the best tool is unavailable. It uses `identity-resolver` to turn the user's PR number, URL, ticket key, or branch into a normalized identity. It normalizes all feedback, triages every item against ticket scope and actual changes, and produces a concise issue board, task list, and report.

The skill does not treat any single tool or provider as the only source of truth for a capability. MCP tools, native binaries, direct APIs, harness tools, and manual fallback are all candidates.

## When to maintain or extend this skill

- The tool-provider taxonomy changes.
- The report schema or state format changes.
- A new built-in tool provider is added.
- The lazy-initialization or checkpointing rules need to change.

## Directory layout

```
pr-report/
├── SKILL.md                    # public contract: type, scope, workflow, hard stops
├── README.md                   # this file
├── config.yaml                 # skill-specific config declaration
├── evals/evals.json            # trigger and behavioral evals
├── scripts/                    # composition test and deterministic helpers
│   └── composition-test.py     # validates conductor wiring without live PRs
├── references/                 # disclosed detail
│   ├── TOOL_SELECTION.md       # capability-to-tool mapping and selection rules
│   ├── REFERENCE.md            # state spec, report schema, normalization, delta rules
│   ├── CONFIG_PATTERN.md       # detect/ask/persist/reuse flow
│   ├── CONTEXT_REPORTS.md      # output schemas and locations
│   ├── COMPOSITION_TEST.md     # composition test and pre-flight checklist
│   ├── DEPENDENCIES.md         # required/recommended skills and tools
│   ├── COMMENT_TRIAGE.md       # source weighting and challenge rules
│   ├── CHECKPOINTING.md        # incremental output and resume rules
│   ├── CHAINLOG.md             # chainlog classification and produced/consumed capabilities
│   ├── WORKFLOW.md             # detailed step sequence
│   ├── EXAMPLES.md             # example reports and states
│   └── VERSIONING.md           # skill and schema version policy
├── subagents/                  # worker prompts
│   ├── normalize-observation.md
│   ├── issue-synthesizer.md
│   ├── report-writer.md
│   └── html-renderer.md
└── assets/
    └── templates/
        └── report-dashboard.html   # optional HTML dashboard template
```

## Key conventions

- Config lives in the detected project config directory (default `{project-root}/.agents/config/pr-report.yaml`), created and migrated by the `initialize-skill` building block.
- Reports and state live in the detected project context directory (default `{project-root}/.agents/context/pr-report/`).
- All provider-specific data comes from the best available tool for each capability; no tool category is treated as the default.
- Tool selection is documented in `references/TOOL_SELECTION.md` and recorded in the report's **Data sources** section.
- The report is written incrementally with `<!-- STATUS: pending/completed -->` markers.
- The `checkpoint` block maintains phase state and current focus after every worker call and after context compaction.
- The skill does not recommend next skills, implement fixes, or resolve threads.

## Tool dependencies

The conductor discovers the best tool for each capability. Examples include:

- **PR metadata, reviews, threads** — GitHub MCP, `gh` CLI, GitHub REST API, manual input.
- **CI / build status** — GitHub MCP (`github_get_check_runs`), `gh` CLI, GitHub Checks API.
- **Static-analysis findings** — SonarCloud/SonarQube MCP, SonarCloud API.
- **Issue tracker scope** — Jira MCP, Jira API, manual input.

The capability matrix and selection hierarchy are in `references/TOOL_SELECTION.md`.

## Shared building blocks

- `detect-project-context` — project root, config directory, and context directory detection.
- `initialize-skill` — first-run config creation and migration.
- `identity-resolver` — normalized PR/ticket/branch/commit resolution.
- `tool-discovery` — capability-first tool discovery and ranking.
- `pr-adapter-contract` — canonical normalized shapes for collected data.
- `worker-contract` — canonical worker return format.
- `token-resolver` — secure token resolution.
- `scope-checker` — in-scope / out-of-scope / ambiguous classification.
- `scan-context` — related context report discovery.
- `checkpoint` — phase checklist and resume state.
- `chainlog` — append-only observation store (producer and consumer).
- `artifact-freshness` — freshness judgment for prior observations and reports.
- `context-reports` — shared context report conventions.

Recommended provider adapters (documented fallback recipes): `github-pr-adapter`, `github-actions-adapter`, `sonarcloud-adapter`, `jira-adapter`, `manual-pr-adapter`.

## Optional context producers

- `debrief` — ticket scope and acceptance criteria.
- `baseline` — pre-change UI or system-state evidence.

## How to update

- Keep `SKILL.md` focused on intent, scope, workflow, and hard stops. Push deep detail into `references/`.
- Prefer updating provider-specific tooling or normalization subagents over changing the conductor when the change is provider-specific.
- Preserve existing user preferences by pre-populating first-run questions with previous defaults.
- Bump the report/state schema version in `references/VERSIONING.md` when artifact structure changes.
