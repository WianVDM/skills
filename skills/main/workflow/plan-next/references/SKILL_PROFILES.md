# Skill Profiling

To recommend skills well, `plan-next` must understand each skill deeply — not just its description.

## First-pass profiling

On first encounter, read:

1. `SKILL.md` — intent, when to use, core workflow, out-of-scope.
2. `references/CAPABILITIES.md` — what the skill detects and consumes.
3. `references/CONTEXT_REPORTS.md` — what it produces.
4. `references/CHECKPOINTING.md` — how heavy/long it is.
5. `references/VALIDATION.md` — when it is considered complete.

Build a profile:

```yaml
name: debrief
triggers:
  - ticket key provided
  - user wants context
inputs:
  - issue tracker data
  - codebase
  - baseline
outputs:
  - .agents/context/debrief/{key}-report.md
cost: heavy
depth: high
verification_value: low
typical_position: understand
notes:
  - "Produces assumptions and confidence rating."
```

## Subsequent passes

To avoid staleness without re-reading everything:

- Re-read `SKILL.md` frontmatter and `references/CHANGELOG.md` if it exists.
- Check if version in metadata changed.
- Re-read full references if the evaluator is uncertain or if the skill changed.
- Otherwise use the cached profile from state.

## Profile fields

| Field | Meaning |
|-------|---------|
| `triggers` | When should this skill activate? |
| `inputs` | What context does it need? |
| `outputs` | What reports does it produce? |
| `cost` | light / medium / heavy |
| `depth` | surface / diagnostic / domain-alignment |
| `verification_value` | Does it confirm correctness? |
| `typical_position` | understand / implement / verify |
| `notes` | Any special considerations |

## Skill relationship map

Capture relationships during profiling:

- **Feeds into:** This skill produces outputs another skill consumes.
- **Alternative to:** This skill can replace another in some contexts.
- **Complements:** This skill works well with another.
- **Precedes:** This skill should run before another.
