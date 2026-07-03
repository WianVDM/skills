# debrief

Build a complete, validated understanding of a ticket.

## Purpose

This is a **conductor skill**. It coordinates focused workers and available context sources to investigate a ticket and produce a structured debrief report. It does not perform the detailed research or codebase exploration itself.

## When to use

- Understand a ticket deeply before planning or implementing.
- Resolve ambiguities through inference and evidence.
- Build shared context for other skills or team members.
- You mention 'debrief', 'understand this ticket', 'get context on ticket', or provide a ticket key without clear next steps.

## Directory layout

```
debrief/
├── SKILL.md                              # main skill instructions
├── README.md                             # this file
├── references/
│   ├── DEPENDENCIES.md                   # required/produced/consumed dependencies
│   ├── CONTEXT_REPORTS.md                # produced/consumed report schemas
│   ├── WORKFLOW.md                       # detailed 13-step workflow reference
│   ├── VERSIONING.md                     # schema and version migration notes
│   ├── WORKER_CONTRACT.md                # standard subagent return contract
│   ├── REFERENCE.md                      # research checklist, state spec, output template
│   ├── CONFIG_PATTERN.md                 # config + notes pattern
│   ├── CAPABILITIES.md                   # available context sources
│   ├── ASSUMPTIONS.md                    # forming and challenging assumptions
│   ├── BASELINE-INTEGRATION.md           # how debrief invokes baseline
│   ├── CHECKPOINTING.md                  # incremental output + resume rules
│   ├── EXAMPLES.md                       # example debriefs
│   ├── VALIDATION.md                     # review checklist
│   ├── harness-specific/                 # modular harness examples
│   │   └── kimi.md
│   └── trackers/                         # issue tracker adapter docs
│       ├── JIRA.md
│       ├── GITHUB.md
│       ├── LINEAR.md
│       └── MANUAL.md
├── subagents/
│   ├── ticket-researcher.md              # gather ticket + related data
│   ├── code-explorer.md                  # resolve ambiguities via codebase
│   ├── assumption-challenger.md          # search for disproof of assumptions
│   ├── synthesis-writer.md               # compile debrief document
│   └── checkpoint-manager.md             # maintain phase checklist and resume state
└── scripts/
    ├── detect-issue-tracker.py           # detect available issue trackers
    ├── extract-ticket-key.py             # extract a ticket key from a branch or text
    ├── check-debrief-freshness.py        # check if a stored report is stale
    └── scan-related-context.py           # scan .agents/context for related reports
```

## Key conventions

- `debrief` is a **conductor skill**: it delegates to focused workers and coordinates the investigation.
- Reports live in `.agents/context/debrief/`.
- Config and notes live in `.agents/config/debrief.yaml`.
- Multiple issue trackers are supported via adapter docs in `references/trackers/`.
- Baseline is required by default when the ticket involves verifiable UI, API, or code state. If baseline cannot proceed, or if it clearly does not apply, consult the user before skipping.
- Assumptions are explicitly formed and challenged before escalation.
- The debrief document is written incrementally to survive context compaction.
- The checkpoint manager maintains phase checklist and resume state.
- Deterministic scripts offset detection, key extraction, and freshness checks.
- The skill uses global defaults only; no project-specific values or harness-specific defaults are shipped with the skill.
- The skill does not recommend next skills.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on intent and move detailed guidance into `references/`. Preserve existing user preferences by pre-populating first-run questions with previous defaults.
