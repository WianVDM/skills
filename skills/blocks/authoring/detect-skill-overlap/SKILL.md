---
name: detect-skill-overlap
description: Detect when a skill overlaps with existing building blocks or contains capabilities that should be extracted as a generic building block. Use when reviewing, auditing, or designing a skill.
invocation: model-invoked
depends:
  - list-available-skills
  - parse-skill-frontmatter
  - index-skill-capabilities
---

# detect-skill-overlap

## Purpose

Compare a target skill against the existing skill catalog and surface duplication and extraction opportunities.

## Type

Building block.

## In scope

- Read the target skill's `SKILL.md`, `README.md`, and all files in `references/`, `subagents/`, `scripts/`, and `assets/`.
- Load the machine-readable capability index using the initializer/lazy-loading pattern:
  - Explicit `--index` argument.
  - `capability_index_path` from `write-a-skill.yaml` config.
  - Project-local override at `.agents/skill-capability-index.json`.
  - Bundle default at `docs/skill-capability-index.json`.
- Validate the index version and freshness; fall back to a description-level index built from the repository files when the index is missing, stale, or malformed.
- Identify capabilities in the target skill that duplicate or overlap with existing building blocks.
- Identify capabilities in the target skill that could be extracted as a generic building block.
- Apply a configurable score threshold to reduce noise.
- Respect recorded false positives provided by the caller.
- Return a structured overlap report with evidence, warnings, and recommendations.

## Out of scope

- This skill does not modify the target skill.
- It does not make the final colocation or extraction decision; it surfaces evidence for the caller to decide.
- It does not install, fetch, or write skill files.
- It does not ask the user directly.
- It does not regenerate the capability index; it only warns when the index is stale and uses the repository fallback.

## When to use

- During skill review or audit to check for duplication.
- During skill design to decide whether to colocate a capability or extract it as a new building block.
- When a conductor needs to know whether a capability already exists in the catalog.

## Steps

1. **Load the target skill.**
   - Read `SKILL.md`, `README.md`, and all files in `references/`, `subagents/`, `scripts/`, and `assets/`.
   - Extract the frontmatter with `parse-skill-frontmatter`.
   - If the target is a design draft, accept it as a JSON entry and skip the file read.
   - **Completion criterion:** target skill content is loaded as a structured index entry.

2. **Load the capability index.**
   - Detect the project context with `detect-project-context` to find the project root and config directory.
   - Load `write-a-skill.yaml` from the config directory if it exists and read `capability_index_path`.
   - Resolve the index path in this order: explicit `--index` argument, configured `capability_index_path`, project-local `.agents/skill-capability-index.json`, bundle default `docs/skill-capability-index.json`.
   - Validate that the file exists, is valid JSON, has a `skills` array, and matches the supported schema version.
   - If the index is stale (skills.json hash mismatch), record a warning but continue using it unless it is malformed.
   - If the index is missing, malformed, or uses an incompatible schema version, fall back to building a description-level index from the repository files by invoking `index-skill-capabilities` logic.
   - Record which index source was used and any warnings in the report.
   - **Completion criterion:** a valid index is available, either from a configured/project-local/bundle file or the fallback.

3. **Find overlaps.**
   - Compare the target skill to every skill in the index except itself.
   - Score overlaps using:
     - Shared capability categories (weighted by category specificity).
     - Shared references, subagents, scripts, config keys, produces, and consumes.
     - Description-level word overlap (always included; primary signal in fallback mode).
   - Apply the caller-provided threshold. Drop scores below the threshold.
   - Exclude any skills listed as false positives by the caller.
   - **Completion criterion:** score-ranked overlap findings list exists.

4. **Find extraction opportunities.**
   - Identify capabilities in the target skill whose category is generic-domain (e.g., `identity-resolution`, `tool-discovery`, `config-initialization`).
   - For each generic capability, count how many existing skills in the index implement the same category.
   - Flag a capability as a strong extraction candidate when it appears in two or more existing skills, has a narrow interface, and is generic-domain.
   - Produce a suggested input/output interface sketch from the category contract and the existing implementations.
   - Estimate effort as `small` or `medium` based on how many skills already implement the capability.
   - **Completion criterion:** extraction candidates list with interface sketches exists.

5. **Produce the report.**
   - Write the overlap report in the format below.
   - Include any warnings about index freshness or fallback mode.
   - **Completion criterion:** report exists and is structured.

## Aggressive stance

This skill is deliberately aggressive. Err on the side of flagging a potential overlap or extraction rather than missing one. The caller will decide whether the finding is a blocker, a warning, or a false positive. Every additional token in a skill must be justified, so any capability that already exists elsewhere or could be reused elsewhere is a finding.

## Overlap signals

Strong overlap signals include:

- The target skill shares one or more capability categories with an existing skill.
- The target skill shares references, subagents, scripts, config keys, or consumes/produces with an existing skill.
- The target skill's description and an existing skill's description are about the same domain.
- The target skill's in-scope items map one-to-one to an existing skill's in-scope items.
- The target skill implements a capability that is already consumed by other skills in the catalog.
- The target skill references the same standards, contracts, or schemas as an existing building block.

## Extraction candidates

Strong extraction signals include:

- A capability in the target skill is used by two or more existing skills in the catalog.
- The capability has a narrow, stable interface (clear inputs and outputs).
- The capability is generic-domain (e.g., path resolution, token handling, context-report formatting) rather than workflow-specific (e.g., "step 3 of the PR report workflow").
- The capability is framed as serving other skills, not just the target skill.

For each extraction candidate, the report includes a **capability contract skeleton**: a draft `SKILL.md` for the proposed building block that the caller can use as a starting point if the user chooses to extract.

## Fallback behavior

When the capability index is unavailable or incompatible:

1. Build a fresh index from the repository files using the same parsing logic as `index-skill-capabilities`.
2. Report a warning that the committed index is missing or stale.
3. Continue overlap detection as normal.

Callers should prefer to regenerate the index when it is stale, but this skill does not fail when the index is out of date.

## False positives

The caller can pass a JSON file of false-positive skill names via `--false-positives`. The file may be either:

- A list of skill names: `["skill-a", "skill-b"]`
- An object with a `false_positives` key: `{"false_positives": ["skill-a", "skill-b"]}`

Flagged skills are excluded from overlap findings. The caller should record the reason for each false positive in the design decision log.

## Output format

```markdown
---
status: complete | partial | blocked
skill: { target-skill-name }
---

# Overlap report: {target-skill-name}

- **Target:** `{target-skill-name}` ({type})
- **Index version:** {version}
- **Overlaps found:** {n}
- **Extraction candidates:** {n}

## Warnings

- {index stale warning, fallback warning, etc.}

## Overlap findings

| Rank | Skill    | Type   | Score   | Shared categories | Shared references |
| ---- | -------- | ------ | ------- | ----------------- | ----------------- |
| 1    | `{name}` | {type} | {score} | {categories}      | {references}      |

## Extraction candidates

### {capability name} (Recommended | Consider)

- **Category:** `{category}`
- **Also appears in:** `{skill-a}`, `{skill-b}`
- **Effort:** small | medium | large
- **Suggested interface:** {one-line summary}

**Interface sketch:**

- Inputs: {list}
- Outputs: {list}
- Description: {one-line}

**Capability contract skeleton:**

```markdown
---
name: {proposed-skill-name}
description: {one-line description}
...
```

## Confidence

- High: strong signal with direct evidence (shared category + shared references + multiple skills).
- Medium: plausible overlap or extraction, but judgment is needed.
- Low: possible match, likely a false positive.
```

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Dependency declaration](references/DEPENDENCIES.md)
- `docs/skill-standards/fundamentals/architecture/dependencies-and-bundling.md` — colocation vs extraction rules.
- `docs/skill-capability-index.json` — machine-readable capability index.
- `skills/blocks/authoring/index-skill-capabilities/references/INDEX_SCHEMA.md` — capability index schema.
