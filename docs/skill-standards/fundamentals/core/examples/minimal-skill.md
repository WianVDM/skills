# Minimal skill

**Layer:** universal fundamentals. **Mode:** reference.

A narrow, model-invoked building block that returns structured output.

```text
find-skills/
├── SKILL.md
└── README.md
```

## `SKILL.md`

```markdown
---
name: find-skills
invocation: model-invoked
description: Discover available skills for the current project and return structured results. Use when a skill or conductor needs to know what skills are available, or when the user asks to find skills.
---

# Find skills

Return a structured list of skills available in the project and user skill directories.

## In scope

- Scan `.agents/skills/` and `~/.agents/skills/`.
- Read each skill's `SKILL.md` frontmatter.
- Return name, description, and type.

## Out of scope

- Do not install skills.
- Do not modify skill files.
- Do not ask the user which skill to pick.

## Output format

Return a markdown list with frontmatter:

---
count: 3
---

- name: review-ui
  description: Review UI code for design-system compliance.
  type: building_block
  invocation: model-invoked

## Dependencies

See references/DEPENDENCIES.md.
```

## Why it works

- **One narrow job:** only discovers skills.
- **Structured output:** conductors can consume the results directly.
- **No side effects:** read-only scan.
- **Explicit dependencies:** required capabilities are documented.

---

## Research basis

See [`../../../reference/sources.md`](../../../reference/sources.md).
