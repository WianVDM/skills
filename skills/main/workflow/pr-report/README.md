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
│   ├── REFERENCE.md            # state spec, report schema, internal normalization model, delta rules
│   ├── CONFIG_PATTERN.md       # detect/ask/persist/reuse flow
│   ├── CONTEXT_REPORTS.md      # output schemas and locations
│   ├── COMPOSITION_TEST.md     # composition test documentation
│   ├── DEPENDENCIES.md         # required/recommended skills and tools
│   ├── COMMENT_TRIAGE.md       # source weighting and challenge rules
│   ├── CHECKPOINTING.md        # incremental output and resume rules
│   ├── WORKFLOW.md             # detailed step sequence
│   ├── VALIDATION.md           # pre-flight checklist
│   ├── EXAMPLES.md             # example reports and states
│   └── VERSIONING.md           # skill and schema version policy
└── subagents/                  # worker prompts
    ├── checkpoint-manager.md
    ├── context-scout.md
    ├── issue-synthesizer.md
    ├── report-writer.md
    ├── html-renderer.md
    ├── scope-checker.md
    ├── normalize-pr.md
    ├── normalize-ci.md
    ├── normalize-static-analysis.md
    └── normalize-issue-tracker.md
```

## Key conventions

- Config lives in the detected project config directory (default `{project-root}/.agents/config/pr-report.yaml`), created and migrated by the `initialize-skill` building block.
- Reports and state live in the detected project context directory (default `{project-root}/.agents/context/pr-report/`).
- All provider-specific data comes from the best available tool for each capability; no tool category is treated as the default.
- Tool selection is documented in `references/TOOL_SELECTION.md` and recorded in the report's **Data sources** section.
- The report is written incrementally with `<!-- STATUS: pending/completed -->` markers.
- The `checkpoint-manager` maintains phase state and current focus after every subagent call and after context compaction.
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
- `context-reports` — shared context report conventions.
- `worker-contract` — canonical worker return format.
- `token-resolver` — secure token resolution.
- `tool-discovery` — capability-first tool discovery and ranking.
- `identity-resolver` — normalized PR/ticket/branch/commit resolution.

## Optional context producers

- `debrief` — ticket scope and acceptance criteria.
- `baseline` — pre-change UI or system-state evidence.

## How to update

- Keep `SKILL.md` focused on intent, scope, workflow, and hard stops. Push deep detail into `references/`.
- Prefer updating provider-specific tooling or normalization subagents over changing the conductor when the change is provider-specific.
- Preserve existing user preferences by pre-populating first-run questions with previous defaults.
- Bump `version` when orchestration or the internal normalization model changes; bump the report/state schema version in `references/VERSIONING.md` when artifact structure changes.
