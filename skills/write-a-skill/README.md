# write-a-skill

A **global, user-invoked conductor skill** for creating, reviewing, and updating skills that follow the skill standards.

## Purpose

Help users produce skills that are focused, portable, composable, and validated before any files are written.

## When to use

Use this skill when you want to:

- **Create a new skill** from scratch.
- **Draft a minimal skill** quickly from a brief description.
- **Review an existing skill** with a verdict-led audit against the fundamentals.
- **Update a skill** to align it with the standards.
- **Decide whether a problem deserves a skill** or a simpler solution (script, MCP server, context file, etc.).

## How to invoke

Reference this skill when discussing skill design. The conductor will classify your intent into one of two top-level branches, then ask one gate question to choose the internal path:

- **create** — for producing a new skill or deciding what shape to build. Internal gates:
  - **full** — complete design workflow for a new skill.
  - **quick** — compressed design workflow for a minimal skill.
  - **decide** — recommendation on whether to build a skill, script, MCP, context file, or reuse an existing skill.
- **change** — for auditing or updating an existing skill. Internal gates:
  - **review** — audit an existing skill and produce a report.
  - **update** — audit an existing skill and optionally apply changes.

The skill is **user-invoked**: type `write-a-skill` or mention it by name when discussing skill design. It does not stay loaded during normal work and no other skill should reach it autonomously.

## Directory layout

```
write-a-skill/
├── SKILL.md                          # conductor: workflow, branches, and gates
├── README.md                         # this file
├── references/                       # condensed standards and guidance
│   ├── FUNDAMENTALS.md               # condensed skill fundamentals
│   ├── PATTERN_HINTS.md              # condensed Layer 2 pattern decision rules
│   ├── BRANCH_WORKFLOWS.md           # detailed per-branch workflows
│   ├── PLUGGABILITY.md               # detection rules and global portability
│   ├── DEPENDENCIES.md               # required building blocks and capabilities
│   ├── STATE_SCHEMA.md               # skill-specific artifact schemas; shared conventions in `context-reports`
│   ├── WORKER_CONTRACT.md            # pointer to the `worker-contract` skill + skill-specific addendum
│   ├── GUIDE_SCRIPT_CURATION.md      # pointer to script guidance + skill-specific addendum
│   ├── GUIDE_EXAMPLES.md             # example skill structures
│   ├── EVAL.md                       # skill-specific trigger, behavioral, and composition eval cases
│   └── GOVERNANCE.md                 # versioning, migration, and maintenance notes for human maintainers
├── subagents/                        # internal worker prompts
│   ├── _TEMPLATE.md                  # shared worker contract, forbidden actions, return format
│   ├── classify-intent.md
│   ├── clarify-scope.md
│   ├── classify-skill-type.md
│   ├── suggest-patterns.md
│   └── draft-skill-md.md
└── assets/templates/                 # starter templates for new skills
    ├── SKILL.md
    ├── README.md
    └── worker-prompt.md
```

## Dependencies

This conductor delegates to the following building blocks:

- `detect-project-context` — project layout detection.
- `list-available-skills` — inventory of existing skills.
- `search-skills-registry` — search for third-party skills.
- `install-skill` — install an existing skill into the project or user scope.
- `decide-skill-shape` — recommend whether a problem should be a new skill, script, MCP, context file, or mode.
- `audit-skill` — standards compliance check.
- `validate-skill-frontmatter` — frontmatter schema validation.
- `review-skill` — audit and remediate an existing skill.
- `run-trigger-evals` — generate trigger evals for model-invoked skills.
- `eval-format` — shared `evals/evals.json` schema and evaluation conventions.
- `parse-skill-frontmatter` — read canonical metadata from a `SKILL.md` file.
- `worker-contract` — shared subagent return contract used when composing worker prompts.
- `context-reports` — shared context-report conventions and schemas.

See `references/DEPENDENCIES.md` for the full declaration.

## Key conventions

- **Conductor, not implementer:** delegates to building-block skills and focused subagents.
- **Design before draft:** no files are written until the user confirms the design and audit.
- **Detection first:** project layout is detected before asking the user; ambiguous detection is confirmed.
- **Global by default:** every design is checked for what blocks it from being a global skill.
- **Scripts-first:** repeatable, deterministic logic is pushed into isolated building-block skills.
- **Fundamentals over guidelines:** the audit rubric in `audit-skill` is the canonical standard; remaining guide files add domain-specific advice only.
- **Self-contained:** ships with condensed fundamentals so it works in any workspace, even without `docs/skill-standards/`.

## Governance

See [references/GOVERNANCE.md](references/GOVERNANCE.md) for versioning policy, migration history, review cadence, and the maintenance checklist.
