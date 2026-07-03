# write-a-skill

A conductor skill for designing, creating, reviewing, and upgrading agent skills.

## Purpose

Help users produce skills that follow the project skill standards: focused, portable, composable, self-configuring, and validated before implementation.

## When to use

Use this skill when you want to:

- Create a new skill from scratch.
- Refactor an existing skill.
- Review a skill against project conventions.
- Decide whether a problem deserves a skill or a simpler solution.
- Upgrade a project-specific skill toward global portability.

## How to invoke

Reference this skill when discussing skill design. The conductor will walk through a structured design process, delegate focused work to subagents, and only draft files after you confirm the design.

## Directory layout

```
write-a-skill/
├── SKILL.md                         # conductor: workflow and gates
├── README.md                        # this file
├── references/                      # skill-level dependencies
│   └── DEPENDENCIES.md
├── subagents/                       # worker personas
│   ├── intent-analyzer.md
│   ├── skill-classifier.md
│   ├── alternative-advisor.md
│   ├── skill-architect.md
│   ├── script-curator.md
│   ├── global-readiness-assessor.md
│   ├── guideline-auditor.md
│   └── skill-drafter.md
└── assets/templates/                # starter templates
    ├── SKILL.md
    ├── README.md
    ├── worker-prompt.md
    └── references/CONFIG_PATTERN.md
```

## Key conventions

- **Conductor, not implementer:** the skill asks, classifies, designs, audits, and drafts through focused workers.
- **Guidelines external:** the project skill standards live in `docs/skill-standards/`. Each subagent reads the relevant canonical document rather than a local copy.
- **Design before draft:** no files are written until the user confirms the design and audit.
- **State preserved:** design artifacts, review reports, and decision logs live in `.agents/context/`.
- **Global-first:** every design is checked for what blocks it from being a global skill.
- **Offset inference:** repeatable logic is pushed into deterministic scripts where appropriate.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on workflow and gates. Update subagent references if the canonical standards in `docs/skill-standards/` change, and keep subagent personas narrow and reusable.
