# pr-report

Build an actionable understanding of a pull request.

## What it does

`pr-report` is a capability-first conductor skill. For every load-bearing capability it needs — PR metadata, review feedback, inline comments, CI/build status, static-analysis findings, and ticket scope — it discovers the available tools, selects the best one, and falls back gracefully when the best tool is unavailable. It normalizes all feedback, triages every item against ticket scope and actual changes, and produces a concise issue board and report.

The skill does not treat its built-in adapters as the only source of truth for any capability. Adapters, MCP tools, native binaries, direct APIs, and manual fallback are all candidates.

## When to maintain or extend this skill

- The adapter taxonomy changes.
- The report schema or state format changes.
- A new built-in adapter is added.
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
│   ├── ADAPTER_ARCHITECTURE.md # adapter taxonomy and discovery model
│   ├── ADAPTER_REGISTRY.md     # default adapter registry
│   ├── REFERENCE.md            # state spec, report schema, delta rules
│   ├── CONFIG_PATTERN.md       # detect/ask/persist/reuse flow
│   ├── CAPABILITIES.md         # tool discovery and lazy loading
│   ├── CONTEXT_REPORTS.md      # output schemas and locations
│   ├── COMPOSITION_TEST.md     # composition test documentation
│   ├── DEPENDENCIES.md         # required/recommended skills and tools
│   ├── COMMENT_TRIAGE.md       # source weighting and challenge rules
│   ├── CHECKPOINTING.md        # incremental output and resume rules
│   ├── WORKFLOW.md             # detailed step sequence
│   ├── VALIDATION.md           # pre-flight checklist
│   ├── EXAMPLES.md             # example reports and states
│   ├── VALIDATION.md           # review checklist
│   └── VERSIONING.md           # skill and schema version policy
└── subagents/                  # worker prompts
    ├── checkpoint-manager.md
    ├── context-scout.md
    ├── issue-synthesizer.md
    ├── report-writer.md
    ├── html-renderer.md
    └── scope-checker.md
```

## Key conventions

- Config lives in the detected project config directory (default `{project-root}/.agents/config/pr-report.yaml`).
- Reports and state live in the detected project context directory (default `{project-root}/.agents/context/pr-report/`).
- All provider-specific data comes from the best available tool for each capability; adapters are one implementation strategy among many.
- Tool selection is documented in `references/TOOL_SELECTION.md` and recorded in the report's **Data sources** section.
- The report is written incrementally with `<!-- STATUS: pending/completed -->` markers.
- The `checkpoint-manager` maintains phase state and current focus after every subagent call and after context compaction.
- The skill does not recommend next skills, implement fixes, or resolve threads.

## Tool dependencies

Built-in adapters are one category of tool consumed by `pr-report`:

- `github-pr-adapter` — PR metadata, files, reviews, threads from GitHub.
- `github-actions-adapter` — CI check runs and logs from GitHub Actions.
- `sonarcloud-adapter` — static-analysis findings from SonarCloud.
- `jira-adapter` — ticket scope and acceptance criteria from Jira.
- `manual-pr-adapter` — fallback for unsupported tools or manual processes.

The conductor also considers MCP tools, native binaries, and direct APIs. The capability matrix is in `references/TOOL_SELECTION.md`.

Shared building blocks:

- `pr-adapter-contract` — normalized adapter interface.
- `token-resolver` — secure token resolution.
- `worker-contract` — canonical worker return format.
- `context-reports` — shared context report conventions.

Optional context producers:

- `debrief` — ticket scope and acceptance criteria.
- `baseline` — pre-change UI or system-state evidence.

## How to update

- Keep `SKILL.md` focused on intent, scope, workflow, and hard stops. Push deep detail into `references/`.
- Prefer updating adapter skills over changing the conductor when the change is provider-specific.
- Preserve existing user preferences by pre-populating first-run questions with previous defaults.
- Bump `metadata.version` when orchestration or the adapter contract changes; bump the report/state schema version in `config.yaml` and `references/VERSIONING.md` when artifact structure changes.
