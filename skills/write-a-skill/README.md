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
│   └── EVAL.md                       # skill-specific trigger and behavioral eval cases
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

## Maintenance and lifecycle

`write-a-skill` tracks its own changes because it is a shared conductor consumed by other skills and workflows. For skills produced by this conductor, `version` is optional unless the user requires it or the skill will be shared or consumed.

`write-a-skill` uses semantic versioning for its own lifecycle:

- **Major bump**: breaking changes to the skill interface, schema, or required capabilities.
- **Minor bump**: new branches, references, or significant backward-compatible workflow improvements.
- **Patch bump**: typo fixes, clarifications, or minor reference updates that do not change behavior.

Current version: **4.7.0**.

Bump the version when state/report schemas change, a new branch or major workflow step is added, subagent behavior changes significantly, or the audit rubric changes in a way that affects ratings. Do not bump for trivial wording fixes. For skills produced by this conductor, only suggest versioning if the user asks for it or if the skill will be distributed/consumed.

### Migration history

- **4.6.0 → 4.7.0**: added a pre-audit comprehension step to the `change` branch using the review principles in `docs/skill-standards/REVIEW_PRINCIPLES.md`; `review-skill` now produces a verdict-led audit report or an incomplete report. Updated the initialization routine to detect canonical standards in `docs/skill-standards/`, `.agents/skill-standards/`, or a configured `standards_path`. No state migration required.
- **4.5.0 → 4.6.0**: extracted the `review` and `update` gates into a new `review-skill` conductor; declared it as a dependency and delegated the `change` branch in `BRANCH_WORKFLOWS.md` to it. No state migration required.
- **4.4.0 → 4.5.0**: extracted the `decide` gate into a new `decide-skill-shape` conductor; declared it as a dependency and delegated the `decide` gate in `BRANCH_WORKFLOWS.md` to it. No state migration required.
- **4.3.0 → 4.4.0**: extracted the shared `evals/evals.json` schema and evaluation conventions into a new `eval-format` vocabulary building block; declared it as a dependency and pointed `EVAL.md` to it. No state migration required.
- **4.2.0 → 4.3.0**: extracted shared context-report conventions (directory layout, envelope, freshness rules, and missing-report handling) into a new `context-reports` vocabulary building block; declared it as a dependency and pointed `STATE_SCHEMA.md` to it. No state migration required.
- **4.1.0 → 4.2.0**: extracted the shared subagent return contract into a new `worker-contract` vocabulary building block; declared it as a dependency and pointed `WORKER_CONTRACT.md` to it. No state migration required.
- **4.0.0 → 4.1.0**: collapsed the five-branch model into two top-level branches (`create` and `change`) with internal gates; updated `BRANCH_WORKFLOWS.md`, `EVAL.md`, and the `classify-intent` subagent to match. No state migration required.
- **3.1 → 4.0**: rewrote the conductor around a 10-phase workflow and five branches (`new`, `quick`, `update`, `review`, `decide`); delegated deterministic work to seven building-block skills; restructured references and contracts. No state migration required; the conductor starts fresh state files.

### Review cadence

- Review this skill after every 10 real-world uses or once per month, whichever comes first.
- Update the audit rubric when the `skill-standards` fundamentals change.
- Add a new eval to `references/EVAL.md` whenever a bug or surprising behavior is observed.
- Run the regression checklist in `references/EVAL.md` before merging any change.

### Maintenance checklist

Before releasing a new version:

- [ ] `SKILL.md` frontmatter version matches the version in this section (only if the skill is versioned).
- [ ] `README.md` reflects the current structure and conventions.
- [ ] All reference links in `SKILL.md` and `README.md` resolve.
- [ ] The audit rubric is still aligned with the target spec.
- [ ] Subagent prompts reference the correct standards and contracts.
- [ ] Trigger and behavioral evals pass.
- [ ] A self-review of `write-a-skill` shows no red principle findings.

## Updating this skill

When modifying this skill, keep `SKILL.md` focused on workflow and gates. Update the rubric in the `audit-skill` building block when standards change, and keep subagent personas narrow, explicit, and reusable.
