# Report schema

Context reports use YAML frontmatter and a markdown body. The frontmatter is the shared envelope; the body is skill-specific.

## Example

```yaml
---
skill: skill-name
version: 1.0.0
key: OC-1234
generated_at: 2026-06-26T08:42:00Z
summary: "One-sentence synthesis."
artifacts:
  - .agents/context/state-capture/OC-1234-main.md
---
```

## Required fields

- `skill` — name of the producing skill.
- `version` — version of the producing skill.
- `key` — report identifier, usually matching the ticket or session key.
- `generated_at` — ISO 8601 timestamp.

## Optional fields

- `summary` — one-sentence synthesis.
- `artifacts` — list of related report paths.

## Consumer declaration

A consuming skill should declare the reports it needs in `references/DEPENDENCIES.md` or in a `consumes` section in `SKILL.md` frontmatter.

```yaml
---
name: project-orchestration
consumes:
  - .agents/context/ticket-research/{key}.md
  - .agents/context/state-capture/{key}-{branch}.md
requires:
  - ticket-research
  - state-capture
---
```
