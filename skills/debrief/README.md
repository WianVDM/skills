# debrief

Investigate and explain a ticket before implementation.

## Purpose

`debrief` is a **conductor / skill base**. It orchestrates focused subagents and available context sources (issue trackers, related work, the codebase, user input, baseline evidence) to understand a ticket and explain it back to the user:

- what the ticket requires
- what assumptions were made
- what evidence supports those assumptions
- what remains unclear

It does not perform the detailed research or codebase exploration itself. It synthesizes the findings into a structured, confidence-rated report.

## Identity

| Attribute | Value |
|---|---|
| **Scope** | `global` |
| **Invocation** | `user-invoked` |
| **Type** | Conductor / orchestrator |
| **Framing** | Investigator and teacher |
| **Success threshold** | 85% confidence with a documented confidence gap |

## When to use

- Understand a ticket deeply before planning or implementing.
- Resolve ambiguities through inference and evidence.
- Build shared context for other skills or team members.
- You mention `debrief`, `understand this ticket`, `get context on ticket`, or provide a ticket key without clear next steps.

## Directory layout

```text
debrief/
├── SKILL.md                              # main skill instructions
├── README.md                             # this file
├── references/
│   ├── DEPENDENCIES.md                   # required/produced/consumed dependencies
│   ├── CONTEXT_REPORTS.md                # report, state, and blocker-report schemas
│   ├── WORKFLOW.md                       # detailed 7-phase workflow reference
│   ├── VERSIONING.md                     # schema and version migration notes
│   ├── WORKER_CONTRACT.md                # standard subagent return contract
│   ├── CONFIG_PATTERN.md                 # config + notes pattern
│   ├── CAPABILITIES.md                   # available context sources
│   ├── ASSUMPTIONS.md                    # forming and challenging assumptions
│   ├── BASELINE-INTEGRATION.md           # how debrief invokes baseline
│   ├── CHECKPOINTING.md                  # incremental output + resume rules
│   ├── EXAMPLES.md                       # example debriefs
│   ├── VALIDATION.md                     # review checklist
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
│   ├── checkpoint-manager.md             # maintain phase checklist and resume state
│   ├── duplicate-detector.md             # detect duplicate or already-implemented tickets
│   ├── task-type-classifier.md           # classify ticket type
│   ├── related-context-scanner.md        # discover related artifacts generically
│   └── baseline-invoker.md               # invoke the baseline skill
└── scripts/
    ├── _frontmatter.py                   # shared robust frontmatter parser
    ├── detect-project-layout.py          # detect project marker directory
    ├── detect-issue-tracker.py           # detect available issue trackers
    ├── extract-ticket-key.py             # extract a ticket key from branch or text
    ├── infer-ticket-type.py              # classify ticket type
    ├── detect-verifiable-state.py        # decide whether baseline is relevant
    ├── scan-related-context.py           # scan context dir for related reports
    ├── check-debrief-freshness.py        # check if a stored report is stale
    ├── find-related-prs.py               # find PRs related to a ticket or files
    └── trace-bug-origin.py               # trace a bug to its original feature commit
```

## Key conventions

- `debrief` is a **global, user-invoked conductor skill**; it delegates to focused subagents and coordinates the investigation.
- Project layout is detected at runtime (`.agents`, `.pi`, `agents`, or user-specified marker). Reports and config use the detected paths, not hardcoded `.agents/`.
- Reports live in `{context_dir}/debrief/`.
- Config and notes live in `{marker_dir}/config/debrief.yaml`.
- Multiple issue trackers are supported; one is active per debrief. Manual fallback is a first-class path.
- The pipeline uses **7 phases**: Bootstrap → Gather evidence → Build context graph → Resolve ambiguities → Baseline → Synthesize → Present.
- Independent subagents run in parallel up to `max_parallel_subagents` (default 3).
- The debrief document is written incrementally to survive context compaction.
- The checkpoint manager maintains phase checklist and resume state.
- Baseline is a **soft default building block** for verifiable state. If unavailable, the user must approve proceeding without it.
- Assumptions are explicitly formed and **grilled** (stress-tested for disproof) before escalation.
- The user is the tie-breaker when evidence is equally split.
- Confidence is calculated from resolved assumptions and remaining ambiguities; below 85% produces a blocker report.
- Deterministic scripts offset detection, key extraction, classification, and freshness checks.
- The skill uses global defaults only; no project-specific values or harness-specific defaults are shipped with the skill.
- The skill does not recommend next skills, implement fixes, write code, or run tests.
- One ticket per invocation; epics are not handled specially.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on intent and move detailed guidance into `references/`. Preserve existing user preferences by pre-populating first-run questions with previous defaults. Run the `write-a-skill` audit rubric before declaring a version complete.

## Maintenance plan

Review this skill after real-world usage or when one of the following occurs:

- A new debrief schema field is added or removed.
- A new subagent or script is introduced.
- The baseline skill or tracker adapters change their contracts.
- A user reports a recurring failure mode not covered by the current reference docs.
- The project-layout detection logic encounters a marker directory not yet handled.

After each review, update `VERSIONING.md`, run the audit rubric, and test the happy path plus one failure mode in a separate workspace project.