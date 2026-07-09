# Wian's Skills

A public repository of agent skills for AI coding assistants.

These skills are built for any harness that supports the [Agent Skills standard](https://agentskills.io/specification) — including pi, Claude Code, OpenAI Codex, Cursor, and others. They provide repeatable workflows for planning, diagnosing, reviewing, and writing code.

> **Status:** most skills in this repo are still in heavy development. Expect interfaces, descriptions, and behavior to change as the library matures.

If you are browsing the source, you will also find the standards these skills follow in `docs/skill-standards/`.

## Quick start

Install the skills with the [`skills`](https://www.npmjs.com/package/skills) CLI:

```bash
npx skills@latest add WianVDM/skills
```

Then open your agent and run the setup skill:

```bash
/setup-wian-skills
```

The setup skill will:

1. Sync the skills into your project or user scope.
2. Resolve shared configuration once.
3. Present a checklist of skills that need project-specific initialization.

Run `/setup-wian-skills` again at any time to check for updates.

## What's in this repo

- `skills/` — the skills themselves, grouped by functional domain. Each leaf directory contains a `SKILL.md` and optional supporting files.
- `docs/manifestos/` — the high-level manifestos: philosophy, architecture.
- `docs/skill-standards/` — the standards these skills follow: format, fundamentals, patterns, evaluation, and governance.

## How to navigate

| You want to... | Start here |
|---|---|
| Install and use these skills | This README, then run `/setup-wian-skills` |
| Understand the standards | [`docs/skill-standards/README.md`](./docs/skill-standards/README.md) |
| Write a new skill | [`docs/skill-standards/README.md`](./docs/skill-standards/README.md) and [`docs/skill-standards/reference/format.md`](./docs/skill-standards/reference/format.md) |
| See available skills | Browse the [`skills/`](./skills) directory |

## Available skill categories

The skills in this repo are grouped into primary functional domains. Because many skills are cross-cutting, a skill's directory is its primary home; its `SKILL.md` metadata and the bundles in `skills.json` describe the rest.

| Domain | Path | Skills |
|---|---|---|
| **Core** | `skills/core/` | `baseline`, `context-reports`, `detect-project-context`, `eval-format`, `token-resolver`, `worker-contract` |
| **Tooling** | `skills/tooling/` | `find-skills`, `install-skill`, `list-available-skills`, `parse-skill-frontmatter`, `search-skills-registry`, `validate-skill-frontmatter` |
| **Adapters** | `skills/adapters/` | `github-pr-adapter`, `github-actions-adapter`, `sonarcloud-adapter`, `jira-adapter`, `manual-pr-adapter` |
| **Authoring** | `skills/authoring/` | `audit-skill`, `decide-skill-shape`, `review-skill`, `run-trigger-evals`, `write-a-skill` |
| **Workflow** | `skills/workflow/` | `debrief`, `handoff`, `merge-latest`, `orchestrate`, `plan-next`, `pr-report`, `to-issues`, `to-prd`, `triage`, `verify-branch` |
| **Engineering** | `skills/engineering/` | `diagnose`, `improve-codebase-architecture`, `prototype`, `tdd` |
| **Modes** | `skills/modes/` | `grill-me`, `grill-with-docs`, `zoom-out` |
| **Setup** | `skills/setup/` | `setup-matt-pocock-skills`, `setup-wian-skills` |

Many skills span multiple domains. For example, `detect-project-context` lives in `core/` but is also used by authoring, workflow, and setup skills. See `skills.json` for the full bundle and dependency breakdown.

## Using a skill

Most skills are invoked by typing their name in the agent:

```bash
/debrief PROJ-123
/tdd
/verify-branch
```

User-invoked skills must be typed explicitly. Model-invoked skills are loaded automatically when the task matches their description.

## Configuration

Configurable skills declare their requirements in a `config.yaml` file. Shared keys are collected once into `.agents/config/shared.yaml` by the setup skill. Skill-specific keys live in `.agents/config/{skill-name}.yaml`.

See [`docs/skill-standards/patterns/configurable.md`](./docs/skill-standards/patterns/configurable.md) and [`docs/skill-standards/reference/config-keys.md`](./docs/skill-standards/reference/config-keys.md) for the convention.

## Documentation

- [`docs/manifestos/philosophy.md`](./docs/manifestos/philosophy.md) — why these skills exist.
- [`docs/manifestos/architecture.md`](./docs/manifestos/architecture.md) — structural layers and composition.
- [`docs/skill-standards/patterns/portability.md`](./docs/skill-standards/patterns/portability.md) — portability across harnesses.
- [`docs/skill-standards/README.md`](./docs/skill-standards/README.md) — the full standards wiki.

## Acknowledgments

This repo takes heavy inspiration from [Matt Pocock's skills](https://github.com/mattpocock/skills), which showed how small, composable skills can shape agent behavior. The `docs/skill-standards/` are also informed by research across agent harnesses, skill registry specifications, and practitioner work in the space.
