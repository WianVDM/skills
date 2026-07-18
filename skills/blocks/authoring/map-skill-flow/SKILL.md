---
name: map-skill-flow
description: Generate a skill's full flow model — branches, gates, phases, success paths, and break points with causes, handling, and confidence. Use when a skill needs its workflow mapped for design, review, comprehension, or eval generation.
invocation: model-invoked
---

# map-skill-flow

## Purpose

Turn a skill into an explicit flow model so a conductor or a human can see what the skill does, where it succeeds, and where it breaks — before relying on it.

## Type

Building block.

## In scope

- Mapping a skill directory (`SKILL.md`, `README.md`, `references/`, `subagents/`) or a design draft into a flow model.
- Extracting declared structure: branches, gates, phases, decision points.
- Inferring implicit branches from prose, with reduced confidence.
- Identifying break points: where the flow can fail, why, and how the skill handles it.
- Returning a flow report, a mermaid diagram, and a break-point list.

## Out of scope

- Judging whether the flow is good (that is `audit-skill` or `review-skill`).
- Modifying the mapped skill. This block is read-only.
- Mapping anything other than a skill or a skill design draft.

## The flow model

For each skill, return:

1. **Branches and gates** — the declared decision structure.
2. **Phases** — the steps per branch with their completion criteria.
3. **Success paths** — what "done" looks like per branch.
4. **Break-point list** — every place the flow can fail, each with:

| Field | Values |
|---|---|
| `cause` | What fails: missing config, missing dependency, ambiguous input, user rejection, degraded source, unmappable input. |
| `detection` | Where in the flow the failure is detected. |
| `handling` | `disclosed` (user is told), `degraded` (falls back with consent), `blocked` (stops with remediation), `silent` (nothing handles it). |
| `confidence` | `declared` (written in the skill) or `inferred` (derived from prose). |

Silent break points are the improvement list. Unhandled failures must be reported, never smoothed over.

## Steps

1. **Load the target.** Read the skill directory or the design draft.
   - **Completion criterion:** all readable files are loaded, or the target is reported `unmappable`.
2. **Extract declared structure.** Branches, gates, phases, and decision points that are written down.
   - **Completion criterion:** declared elements are labeled `declared`.
3. **Infer implicit structure.** Branches and decisions implied by prose but not declared.
   - **Completion criterion:** inferred elements are labeled `inferred`.
4. **Map failure paths.** For each phase and decision point, identify what can break, where it is detected, and how the skill handles it.
   - **Completion criterion:** every break point has cause, detection, handling, and confidence.
5. **Return the model.** Flow report, mermaid diagram, break-point list.
   - **Completion criterion:** the flow report follows the schema in [references/FLOW_MODEL.md](references/FLOW_MODEL.md).

If the input cannot be mapped (not a skill, unreadable, empty), return `blocked` with what is missing. Do not invent a flow for an unmappable input.

## Output format

- A mermaid `flowchart` of branches, gates, and phases.
- A flow report (markdown context report) per [references/FLOW_MODEL.md](references/FLOW_MODEL.md).
- A break-point list sorted by handling (`silent` first).

## Security

- Read-only. Never writes to the mapped skill.
- Flow reports are written to the caller's context directory, never into the target skill.

## Dependencies

None required. When available, `context-reports` conventions govern the flow report envelope.

## Research basis

Original to this repo: the flow model, break-point classification, and confidence labeling, derived from the degradation ladder and failure-mode taxonomy in the skill standards.
