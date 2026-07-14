# Wian's Skills

A public collection of agent skills for AI coding assistants.

These skills work with any harness that supports the [Agent Skills standard](https://agentskills.io/specification). They give you repeatable workflows for understanding tickets, planning work, reviewing code, diagnosing bugs, and writing new skills.

## Main skills

The main skills are the ones you invoke directly. Selecting one in the [Vercel skills CLI](https://www.npmjs.com/package/skills) automatically installs its block-skill dependencies.

| Skill | Invocation | What it does |
|---|---|---|
| `baseline` | `model-invoked` | Capture a reproducible snapshot of a feature, module, route, API, or bug. |
| `debrief` | `model-invoked` | Understand a ticket before implementation. |
| `diagnose` | `/diagnose` | Run a disciplined diagnosis loop for hard bugs and performance regressions. |
| `grill-me` | `/grill-me` | Stress-test a plan or design by questioning every branch. |
| `grill-with-docs` | `/grill-with-docs` | Stress-test a plan against the project's domain model and update docs inline. |
| `handoff` | `/handoff` | Write a session snapshot for a fresh session to continue from. |
| `improve-codebase-architecture` | `/improve-codebase-architecture` | Find deepening opportunities in a codebase. |
| `merge-latest` | `/merge-latest` | Merge the latest upstream branch safely. |
| `orchestrate` | `/orchestrate` | Move a ticket from context to completed implementation. |
| `plan-next` | `/plan-next` | Discover available skills and build a phased action plan. |
| `pr-report` | `model-invoked` | Build an actionable understanding of a pull request. |
| `prototype` | `/prototype` | Build a throwaway prototype to test a design. |
| `tdd` | `/tdd` | Run a test-driven development red-green-refactor loop. |
| `to-issues` | `/to-issues` | Break a plan into independently-grabbable issues. |
| `to-prd` | `/to-prd` | Turn conversation context into a PRD. |
| `triage` | `/triage` | Triage issues through a state machine of roles. |
| `verify-branch` | `/verify-branch` | Verify that changed code will pass CI gates. |
| `write-a-skill` | `/write-a-skill` | Design, review, and update skills that follow the standards. |
| `zoom-out` | `/zoom-out` | Ask the agent to zoom out and give a higher-level perspective. |

For the full list, including block skills and dependencies, see [docs/skill-catalog.md](docs/skill-catalog.md).

## Quick start

1. Install the bundle with the skills CLI:

   ```bash
   npx skills@latest add WianVDM/skills
   ```

2. Run the setup skill in your agent:

   ```bash
   /setup-wian-skills
   ```

3. Invoke a main skill. For example, `/debrief` or `/plan-next`.

## How this repo is organized

- `skills/main/` — user-facing skills.
- `skills/blocks/` — reusable building blocks that main skills compose.
- `skills/setup/` — setup and sync utilities.
- `docs/manifestos/` — the ideas behind the library.
- `docs/skill-standards/` — rules and patterns for writing skills.
- `docs/skill-catalog.md` — full list of every skill.
- `skills.json` — the bundle manifest and dependencies.
- `scripts/generate-skill-catalog.py` — regenerates `docs/skill-catalog.md` from `skills.json` and each `SKILL.md`.

## Documentation

- [Skill catalog](docs/skill-catalog.md) — every skill, with invocation and dependencies.
- [Design philosophy](docs/manifestos/philosophy.md)
- [Skill standards](docs/skill-standards/README.md)
- [Skill format](docs/skill-standards/reference/format.md)
- [Dependencies and bundling](docs/skill-standards/fundamentals/architecture/dependencies-and-bundling.md)

## Status

Most skills are in active development. Expect interfaces, descriptions, and behavior to change.

## Acknowledgments

This repo takes heavy inspiration from [Matt Pocock's skills](https://github.com/mattpocock/skills).
