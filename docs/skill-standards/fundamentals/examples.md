# Examples

These examples show how the fundamentals apply to real skill shapes. They are illustrative, not exhaustive. For pattern-specific examples, see the relevant pattern document:

- [Building-block examples](../patterns/building-block.md)
- [Conductor examples](../patterns/conductor.md)
- [Discipline-skill examples](../patterns/discipline-skill.md)
- [Context-file examples](../patterns/context-file.md)
- [Configurable-skill examples](../patterns/configurable.md)
- [Initialization examples](../patterns/initialization.md)

---

## Example 1 — Minimal `SKILL.md`

A narrow, model-invoked building block that returns structured output.

```text
find-skills/
├── SKILL.md
└── README.md
```

### `SKILL.md`

```markdown
---
name: find-skills
version: 1.0.0
metadata:
  author: tooling-team
invocation: model-invoked
description: Discover available skills for the current project and return structured results. Use when a skill or conductor needs to know what skills are available, or when the user asks to find skills.
---

# Find skills

Return a structured list of skills available in the project and user skill directories.

## In scope

- Scan `.agents/skills/` and `~/.agents/skills/`.
- Read each skill's `SKILL.md` frontmatter.
- Return name, description, version, and type.

## Out of scope

- Do not install skills.
- Do not modify skill files.
- Do not ask the user which skill to pick.

## Output format

Return a markdown list with frontmatter:

```yaml
---
count: 3
---

- name: review-ui
  description: Review UI code for design-system compliance.
  version: 1.0.0
  type: building_block
  invocation: model-invoked
```

## Dependencies

See references/DEPENDENCIES.md.
```

### Why it works

- **One narrow job:** only discovers skills.
- **Structured output:** conductors can consume the results directly.
- **No side effects:** read-only scan.
- **Explicit dependencies:** required capabilities are documented.

---

## Example 2 — `references/DEPENDENCIES.md`

```markdown
# Dependencies

## Required skills

- `state-capture` — for capturing initial UI or system state.

## Consumed reports

- `.agents/context/state-capture/{key}.md`

## Required tools

- Access to the project's issue tracker.
- Ability to read source files and documentation.
```

### Why it works

- **Dependencies are explicit.** Nothing is hidden.
- **Skills and reports are separated.** Consumers know what skills produce the reports they need.
- **Capabilities are stated.** A maintainer can see what the skill expects from the environment.

---

## Example 3 — Worker prompt

A focused worker for a conductor or multi-layer skill.

```markdown
# Investigator

You are an investigator worker for the `ticket-research` skill.

Your job: explore the codebase and identify files and decisions relevant to a ticket.

## In scope

- Read source files, tests, ADRs, and docs.
- Identify files likely to change.
- Note architectural constraints.

## Out of scope

- Do not propose fixes.
- Do not write code.
- Do not ask the user questions.

## Tools you may use

- Read files.
- Search the codebase.

## Return format

Use the standard worker return contract.

```yaml
---
status: complete | partial | needs_input | blocked
artifacts:
  - path/to/artifact.md
---

## Summary
...

## Findings
- ...

## Decisions made
- ...

## Open questions
- ...

## Blockers
- ...
```
```

### Why it works

- **Role and scope are explicit.** The worker knows exactly what to do.
- **Boundaries are clear.** It knows what not to do.
- **Tools are listed.** It does not have to guess what it can use.
- **Return format is fixed.** The conductor can integrate the output reliably.

---

## Example 4 — Config evolution

A skill's config should adapt to what it learns.

### Initial config

```yaml
# .agents/config/example-skill.yaml

preferences:
  sonarqube:
    method: mcp

notes: []
```

### After first run

The agent discovers the MCP server cannot export issues. It asks the user, then updates:

```yaml
# .agents/config/example-skill.yaml

preferences:
  sonarqube:
    method: api
    url: https://sonar.example.com
    token_env: SONAR_TOKEN

notes:
  - text: "MCP server lacks issue-export scope. Use web API with SONAR_TOKEN instead."
    category: workaround
    added: "2026-06-26"
```

### Why it works

- The skill adapts to the actual environment.
- Future invocations skip the discovery step.
- The reasoning is recorded, not just the setting.
