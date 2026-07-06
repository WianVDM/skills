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

- `skills/` — the skills themselves. Each directory contains a `SKILL.md` and optional supporting files.
- `docs/skill-standards/` — the standards these skills follow: format, fundamentals, patterns, evaluation, and governance.

## How to navigate

| You want to... | Start here |
|---|---|
| Install and use these skills | This README, then run `/setup-wian-skills` |
| Understand the standards | [`docs/skill-standards/README.md`](./docs/skill-standards/README.md) |
| Write a new skill | [`docs/skill-standards/README.md`](./docs/skill-standards/README.md) and [`docs/skill-standards/FORMAT.md`](./docs/skill-standards/FORMAT.md) |
| See available skills | Browse the [`skills/`](./skills) directory |

## Available skill categories

- **Workflow**: `debrief`, `orchestrate`, `plan-next`, `pr-report`, `handoff`, ...
- **Code quality**: `diagnose`, `tdd`, `verify-branch`, `audit-skill`, `review-skill`, ...
- **Architecture**: `improve-codebase-architecture`, `prototype`, `detect-project-context`, ...
- **Authoring**: `write-a-skill`, `audit-skill`, `validate-skill-frontmatter`, ...
- **Utilities**: `find-skills`, `list-available-skills`, `install-skill`, `baseline`, ...

See the [`skills/`](./skills) directory for the complete list. Each skill's `SKILL.md` describes what it does and how to invoke it.

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

See [`docs/skill-standards/patterns/configurable.md`](./docs/skill-standards/patterns/configurable.md) and [`docs/skill-standards/CONFIG_KEYS.md`](./docs/skill-standards/CONFIG_KEYS.md) for the convention.

## Documentation

- [`docs/PHILOSOPHY.md`](./docs/PHILOSOPHY.md) — why these skills exist.
- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — structural layers and composition.
- [`docs/PORTABILITY.md`](./docs/PORTABILITY.md) — portability across harnesses.
- [`docs/skill-standards/README.md`](./docs/skill-standards/README.md) — the full standards wiki.

## Acknowledgments

This repo takes heavy inspiration from [Matt Pocock's skills](https://github.com/mattpocock/skills), which showed how small, composable skills can shape agent behavior. The `docs/skill-standards/` are also informed by research across agent harnesses, skill registry specifications, and practitioner work in the space.
