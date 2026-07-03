# write-a-skill

A **global, user-invoked conductor skill** for designing, drafting, reviewing, and upgrading agent skills. It follows the `skill-standards` fundamentals: one core objective, explicit boundaries, declared dependencies, and validation before implementation.

## Purpose

Help users produce skills that are focused, portable, composable, self-configuring, and validated before any files are written.

## When to use

Use this skill when you want to:

- **Create a new skill** from scratch.
- **Draft a minimal skill** quickly from a brief description.
- **Review an existing skill** against the fundamentals.
- **Upgrade a project-specific skill** toward global portability.
- **Decide whether a problem deserves a skill** or a simpler solution (script, MCP server, prompt template, etc.).

## How to invoke

Reference this skill when discussing skill design. The conductor will classify your intent into one of four branches:

- **New** — full design workflow for a new skill.
- **Quick** — compressed design workflow for a minimal skill.
- **Review** — audit an existing skill and produce a report.
- **Upgrade** — plan and optionally apply changes to make a skill global-ready.

The skill is **user-invoked**: type `write-a-skill` or mention it by name when discussing skill design. It does not stay loaded during normal work and no other skill should reach it autonomously. The frontmatter declares both `invocation: user-invoked` and `disable-model-invocation: true`.

## Directory layout

```
write-a-skill/
├── SKILL.md                          # conductor: workflow, branches, and gates
├── README.md                         # this file
├── scripts/
│   └── detect-project-layout.py      # deterministic project layout detection
├── references/                       # standards, schemas, and guidance
│   ├── AUDIT_RUBRIC.md               # A–K criteria for skill review
│   ├── BRANCH_WORKFLOWS.md           # detailed per-branch workflows
│   ├── PLUGGABILITY.md               # detection rules and global portability
│   ├── DEPENDENCIES.md               # required capabilities and assumptions
│   ├── STATE_SCHEMA.md               # artifact schemas
│   ├── CONTEXT_REPORTS.md            # report schemas and freshness rules
│   ├── SELF_AUDIT_CHECKLIST.md       # pre-draft fundamentals check
│   ├── WORKER_CONTRACT.md             # standard subagent return format
│   ├── GLOSSARY.md                   # shared vocabulary
│   ├── GUIDE_SCRIPT_CURATION.md      # when to use scripts
│   ├── GUIDE_EXAMPLES.md             # example skill structures
│   ├── EVAL.md                       # trigger and behavioral evals
│   └── MAINTENANCE.md                # versioning, migration, and review cadence
├── subagents/                        # worker personas for each branch
│   ├── branch-classifier.md
│   ├── intent-analyzer.md
│   ├── skill-classifier.md
│   ├── alternative-advisor.md
│   ├── skill-architect.md
│   ├── script-curator.md
│   ├── global-readiness-assessor.md
│   ├── guideline-auditor.md
│   ├── skill-reviewer.md
│   ├── skill-upgrader.md
│   └── skill-drafter.md
└── assets/templates/                 # starter templates for new skills
    ├── SKILL.md
    ├── README.md
    ├── worker-prompt.md
    └── references/
        ├── CONFIG_PATTERN.md
        ├── CONTEXT_REPORTS.md
        └── WORKER_CONTRACT.md
```

## Key conventions

- **Conductor, not implementer:** the skill asks, classifies, designs, audits, and drafts through focused workers.
- **Design before draft:** no files are written until the user confirms the design and audit.
- **Detection first:** project layout is detected before asking the user; ambiguous detection is confirmed.
- **Global by default:** every design is checked for what blocks it from being a global skill.
- **Scripts-first:** repeatable, deterministic logic is pushed into isolated scripts.
- **Fundamentals over guidelines:** the audit rubric is the canonical standard; remaining guide files add domain-specific advice only.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on workflow and gates. Update the rubric when standards change, and keep subagent personas narrow, explicit, and reusable.
