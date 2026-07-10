# detect-skill-overlap

A building block that compares a skill against the existing skill catalog and surfaces duplication and extraction opportunities.

## When to use

- You are reviewing or auditing a skill and want to know if it duplicates an existing building block.
- You are designing a skill and want to decide whether a capability should be colocated or extracted.
- You need evidence about whether a capability already exists in the catalog.

## How to use

Invoke `detect-skill-overlap` with the path to the skill under review. The skill loads the target skill, loads the catalog via `list-available-skills`, and returns a structured overlap report.

## Example output

```markdown
---
status: complete
skill: my-new-skill
---

# Overlap report: my-new-skill

## Overlap findings

| ID | Type | Existing skill | Capability | Evidence | Recommendation |
|---|---|---|---|---|---|
| O-01 | overlap | parse-skill-frontmatter | Extract YAML frontmatter | Target skill parses `SKILL.md` headers | Reuse `parse-skill-frontmatter` instead. |

## Extraction candidates

| ID | Capability | Generic value | Likely consumers | Interface sketch |
|---|---|---|---|---|
| E-01 | Token resolution | Used by many adapters | github-pr-adapter, jira-adapter | Input: env var name; Output: token reference |
```

## Dependencies

- `list-available-skills` — catalog loader.
- `parse-skill-frontmatter` — frontmatter extractor.

See `references/DEPENDENCIES.md` for the full list.
