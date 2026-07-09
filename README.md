# Wian's Skills

A public collection of agent skills for AI coding assistants.

These skills are built for any harness that supports the [Agent Skills standard](https://agentskills.io/specification). They provide repeatable workflows for planning, diagnosing, reviewing, and writing code.

> **Status:** Most skills are in heavy development. Expect interfaces, descriptions, and behavior to change.

## Quick start

Install the skills with the [skills CLI](https://www.npmjs.com/package/skills):

```bash
npx skills@latest add WianVDM/skills
```

Then run the setup skill in your agent:

```bash
/setup-wian-skills
```

## What's in this repo

- `skills/` — the skills themselves, grouped by domain.
- `docs/manifestos/` — the high-level ideas behind the library.
- `docs/skill-standards/` — the rules, patterns, and reference for writing skills.
- `skills.json` — the full bundle and dependency breakdown.

## Where to start

| You want to... | Start here |
|---|---|
| Install or update these skills | This README, then run `/setup-wian-skills` |
| Browse available skills | `skills.json` or the `skills/` directory |
| Understand the design | `docs/manifestos/philosophy.md` |
| Write a new skill | `docs/skill-standards/README.md` |
| Review the standards | `docs/skill-standards/reference/format.md` |

## Acknowledgments

This repo takes heavy inspiration from [Matt Pocock's skills](https://github.com/mattpocock/skills).
