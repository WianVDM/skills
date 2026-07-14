---
name: detect-skill-overlap
description: Detect when a skill overlaps with existing building blocks or contains capabilities that should be extracted as a generic building block. Use when reviewing, auditing, or designing a skill.
version: 1.0.0
invocation: model-invoked
depends:
  - list-available-skills
  - parse-skill-frontmatter
---

# detect-skill-overlap

## Purpose

Compare a target skill against the existing skill catalog and surface duplication and extraction opportunities.

## Type

Building block.

## In scope

- Read the target skill's `SKILL.md`, `README.md`, and all files in `references/`, `subagents/`, `scripts/`, and `assets/`.
- Load the existing skill catalog via `list-available-skills`.
- Identify capabilities in the target skill that duplicate or overlap with existing building blocks.
- Identify capabilities in the target skill that could be extracted as a generic building block.
- Return a structured overlap report with evidence and recommendations.

## Out of scope

- This skill does not modify the target skill.
- It does not make the final colocation or extraction decision; it surfaces evidence for the caller to decide.
- It does not install, fetch, or write skill files.
- It does not ask the user directly.

## When to use

- During skill review or audit to check for duplication.
- During skill design to decide whether to colocate a capability or extract it as a new building block.
- When a conductor needs to know whether a capability already exists in the catalog.

## Steps

1. **Load the target skill.**
   - Read `SKILL.md`, `README.md`, and all files in `references/`, `subagents/`, `scripts/`, and `assets/`.
   - Extract the frontmatter with `parse-skill-frontmatter`.
   - **Completion criterion:** target skill content is loaded.

2. **Load the catalog.**
   - Run `list-available-skills` to get the project and user scope.
   - Read the `SKILL.md` and `skills.json` of each catalog skill, especially building blocks and vocabulary skills.
   - Count how many other skills depend on each building block.
   - **Completion criterion:** catalog is loaded and dependency relationships are understood.

3. **Find overlaps.**
   - Compare the target skill's purpose, scope, capabilities, and references to each catalog skill.
   - Flag an overlap if any of the following are true:
     - The descriptions name the same or adjacent domain.
     - The in-scope lists cover the same capabilities.
     - The target skill duplicates a capability already provided by a catalog skill.
     - The target skill uses different words but solves the same problem.
   - Provide evidence: quoted capability, matching skill name, and dependency count.
   - **Completion criterion:** overlap findings list exists.

4. **Find extraction opportunities.**
   - Identify capabilities in the target skill that are:
     - Cross-cutting (likely to be useful to multiple skills).
     - Framed as a stable, narrow interface.
     - Solving a generic-domain problem rather than a workflow-specific problem.
   - Flag an extraction candidate if it is not already a standalone skill and meets the criteria.
   - Provide evidence: which other skills would consume it, what the interface would be.
   - **Completion criterion:** extraction findings list exists.

5. **Produce the report.**
   - Write the overlap report in the format below.
   - **Completion criterion:** report exists and is structured.

## Aggressive stance

This skill is deliberately aggressive. Err on the side of flagging a potential overlap or extraction rather than missing one. The caller will decide whether the finding is a blocker, a warning, or a false positive. Every additional token in a skill must be justified, so any capability that already exists elsewhere or could be reused elsewhere is a finding.

## Overlap signals

Strong overlap signals include:

- The target skill's description and an existing skill's description are about the same domain.
- The target skill's in-scope items map one-to-one to an existing skill's in-scope items.
- The target skill implements a capability that is already consumed by other skills in the catalog.
- The target skill references the same standards, contracts, or schemas as an existing building block.

## Extraction signals

Strong extraction signals include:

- A capability in the target skill is used by two or more existing skills in the catalog.
- The capability has a narrow, stable interface (e.g., parse a file, resolve a token, detect a project root).
- The capability is generic-domain (e.g., path resolution, token handling, context-report formatting) rather than workflow-specific (e.g., "step 3 of the PR report workflow").
- The capability is framed as serving other skills, not just the target skill.

## Output format

```markdown
---
status: complete | partial | blocked
skill: {target-skill-name}
---

# Overlap report: {target-skill-name}

## Overlap findings

| ID | Type | Existing skill | Capability | Evidence | Recommendation |
|---|---|---|---|---|---|
| O-01 | overlap | {name} | {capability} | {quote or dependency count} | Reuse, extend, or merge with the existing skill. |

## Extraction candidates

| ID | Capability | Generic value | Likely consumers | Interface sketch |
|---|---|---|---|---|
| E-01 | {capability} | {why it is generic} | {skills that would use it} | {input/output contract} |

## Confidence

- High: strong signal with direct evidence.
- Medium: plausible overlap or extraction, but judgment is needed.
- Low: possible match, likely a false positive.
```

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Dependency declaration](references/DEPENDENCIES.md)
- `docs/skill-standards/fundamentals/architecture/dependencies-and-bundling.md` — colocation vs extraction rules.
