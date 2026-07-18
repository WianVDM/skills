---
name: write-a-skill
description: Design, review, and update skills that follow the skill standards. Use when creating a new skill, auditing or refining an existing one, clarifying a vague skill idea, or deciding what shape an idea should take.
invocation: user-invoked
depends:
  - audit-skill
  - context-reports
  - decide-skill-shape
  - detect-project-context
  - eval-format
  - parse-skill-frontmatter
  - review-skill
  - validate-skill-frontmatter
  - worker-contract
  - artifact-freshness
  - chainlog
  - detect-skill-overlap
  - install-skill
  - list-available-skills
  - map-skill-flow
  - run-trigger-evals
  - search-skills-registry
  - token-resolver
---

# write-a-skill

## Purpose

Help the user produce a skill that satisfies the skill fundamentals and applies the right architecture patterns.

## In scope

- Clarifying a vague idea or rough draft into a confirmed objective map, without writing files.
- Creating new skills from scratch.
- Drafting minimal skills quickly from a brief description.
- Reviewing existing skills against the fundamentals, after first understanding their purpose, shape, scope, and token economy.
- Updating existing skills to align with the standards.
- Recommending the right shape (skill, script, MCP server, context file, or mode) when the user is unsure.
- Delegating detection, audit, and validation to standalone building-block skills.
- Writing context reports and, after explicit approval, skill files.

## Out of scope

- This skill does not write application code; it only produces skill files, references, and context reports.
- It does not install or modify skills without explicit user approval; confirm every install, overwrite, or update before applying it.
- It does not choose a solution on the user's behalf without first exploring alternatives; present options with a recommended default.
- It does not replace the user's judgment on whether a skill is needed; ask the user to confirm the design decision before drafting.

## Type

Conductor. `write-a-skill` coordinates multiple building-block skills and subagents to produce, audit, and update skills. It delegates deterministic work to standalone skills and uses focused subagents only for tightly coupled design judgment.

## Portability and invocation

- **Invocation mode:** user-invoked. This is a meta-design conversation and should not stay loaded during normal work.
- **Scope:** global. It must work in any project with any harness.
- **Pluggability:** the skill detects the project layout and always confirms before writing files. See [references/PLUGGABILITY.md][pluggability].
- **Standards path:** the skill resolves canonical standards through configuration, project-context detection, or user consent. See the `standards-path` fundamental and the shared resolver.
- **No hardcoded project paths:** paths are resolved through detection, configuration, or user confirmation.
- **Self-contained:** the skill ships with condensed fundamentals in [references/FUNDAMENTALS.md][fundamentals] and [references/PATTERN_HINTS.md][pattern-hints]. It can optionally bootstrap the full standards from a public repository on first run.

## Branch entry

Classify the user's intent into one top-level branch. If the intent is unclear, ask one clarifying question with a proposed default.

| Branch         | Trigger                                                                 | Internal gate                | Outcome                                                                   |
| -------------- | ----------------------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------- |
| **initialize** | No `write-a-skill.yaml` config exists, or the user asks to reconfigure. | `config`                     | A persisted `write-a-skill.yaml` with project paths and standards source. |
| **explore**    | User has a vague idea or rough draft and wants clarity before building. | none                         | A confirmed objective map and a recommendation; no files written.          |
| **create**     | User wants to produce a new skill.                                      | `full` or `quick`            | A designed and audited new skill.                                          |
| **change**     | User wants to audit or refine an existing skill.                        | `review` or `update`         | An audit report, or a remediation plan with optional changes.             |

**Completion criterion:** the branch is one of {initialize, explore, create, change} and the user has confirmed or corrected the default.

## Workflow

The conductor runs this pipeline. Each phase has a completion criterion and a decision gate. Phases may be compressed for the `quick` gate. Every branch starts at phase 0; `explore` exits after its recommendation.

| Phase | What happens | Completion criterion |
|---|---|---|
| 0. **Objective map** | Build the objective map with the user via `map-objective` (prefill-and-confirm; grill only the gaps). See [references/OBJECTIVE_MAP.md][objective-map]. For `explore`, sketch the idea's flow with `map-skill-flow`, continue to alternatives and a recommendation, then stop. | The map is confirmed by the user and persisted to the intent note. For `explore`: a flow sketch and a recommendation exist; no files were written. |
| 1. **Choose gate** | Classify the branch and internal gate via `classify-intent`; ask one question at a time if unclear. | Branch is one of {initialize, explore, create, change}, gate is resolved, and user confirmed. |
| 2. **Explore alternatives** | Use `list-available-skills`, `search-skills-registry`, and `detect-skill-overlap` to see what exists and flag overlap. Write the structured overlap findings to `{context}/skill-design/{skill-name}-overlap-findings.md`. If the proposed skill duplicates a `chainlog` capability, recommend reuse over private storage. | Alternatives report exists; overlap findings report exists; chainlog overlap is noted; user knows whether to create, reuse, or install. |
| 3. **Decide shape and colocation** | Decide whether the answer is a new skill, an existing skill, a script, an MCP server, or a context file. Use the overlap findings to present three options per significant overlap: **reuse**, **colocate**, or **extract** a shared building block. | User confirms the chosen shape and the reuse/colocate/extract decision for each significant overlap; extraction candidates have interface sketches. |
| 4. **Define identity** | Name and invocation. | Name matches the directory, invocation is chosen deliberately, and user confirmed. |
| 5. **Define scope** | In-scope, out-of-scope, branches, assumptions. | Scope boundaries are explicit and defensible. |
| 6. **Description design** | Design the description as the routing surface: leading word or domain first, one trigger per distinct branch from the map's triggers field, a reach clause if other skills consume it, ≤ 1024 characters. | Description follows the canonical shape and the user confirmed it. |
| 7. **Select patterns** | Apply fundamentals; suggest Layer 2 patterns. Ask the chainlog classification question; if not `neither`, invoke `check-chainlog-needs` and confirm work item types, capabilities, and storage adapter strategy. Decide if the skill is configurable and which config keys it needs. | Pattern list and config declaration (if any) exist; chainlog classification and details are confirmed; user confirmed. |
| 7a. **Pattern adherence** | Compare the chosen patterns against the canonical skill-standards docs; flag deviations before drafting. | Pattern list is mapped to canonical pattern documents; deviations are recorded with rationale. |
| 7b. **Design capability-to-tool strategy** | For each load-bearing capability, identify the preferred tool, fallback tools, and degraded-output disclosure. Document the selection rule and user-consent behavior. | A capability-to-tool mapping exists for every load-bearing capability; the user has confirmed or corrected the strategy. |
| 8. **Token justification** | Defend every proposed section, reference, subagent, and script; remove or merge unjustified items. | Every artifact in the draft has a stated purpose; the user has confirmed the minimal set. |
| 8a. **Flow gate** | Generate the pre-draft flow with `map-skill-flow` from the confirmed design; review the break points with the user. Silent breaks are resolved in the design or explicitly accepted. | Flow diagram exists; break points are reviewed; the user confirms the design still holds. |
| 9. **Draft artifacts** | Generate `SKILL.md`, optional `README.md`, `references/`, `subagents/`, `scripts/`, `assets/`, and `config.yaml` if the skill is configurable. If the chainlog classification is not `neither`, copy the appropriate `references/chainlog-template-{producer,consumer,both}.md` to `references/CHAINLOG.md` and fill the placeholders. | Draft files exist and are linked correctly; `references/CHAINLOG.md` exists if applicable. |
| 10. **Audit and validate** | Run `audit-skill` and `validate-skill-frontmatter`. Re-run `detect-skill-overlap` if capabilities changed during drafting. | Audit report exists with no blocking failures. |
| 11. **Generate evals** | Run `run-trigger-evals` for model-invoked skills. | `evals/evals.json` exists or user declined. |
| 12. **Confirm and write** | Present the full plan with the flow diagram rendered; write files only after explicit approval. | User approved the visible flow, not a wall of prose; files written; decision log updated. |

## Tooling-awareness design checklist

This checklist is load-bearing. The conductor must confirm each applicable item explicitly with the user before moving to the Draft phase. If an item does not apply, record the rationale in the decision log.

- **Outcome first.** Every load-bearing capability step names the outcome before choosing a tool.
- **Tool discovery.** The skill detects available tools across all categories (skill adapters, MCP servers, native binaries, direct APIs, harness tools, manual fallback).
- **Best available tool.** The skill prefers the best available tool, not just the adapter it ships with.
- **Documented selection.** The preferred tool, fallback tools, and selection rule are documented.
- **Degraded disclosure.** If a degraded source is used, the skill tells the user what better option was available and gets explicit or recorded consent.
- **Dependency surface.** The full dependency surface is declared in `references/DEPENDENCIES.md` and `skills.json`.

For the chainlog design checklist — classification, producer/consumer checks, freshness, schema, identity, storage adapter, report linkage, secrets — see [references/CHAINLOG_DESIGN.md](references/CHAINLOG_DESIGN.md).

## Colocation and extraction checklist

Before deciding a new skill is needed, the conductor must confirm:

- **Reuse justification.** The capability is used by more than one skill, or is a cross-cutting concern, or has a stable narrow interface, or solves a generic-domain problem.
- **No speculative extraction.** The capability is not being extracted only because it is "self-contained" or "might be useful someday."
- **Single-consumer warning.** If the capability is only used by one existing skill, the user has explicitly agreed that a separate skill is justified.
- **Identity framing.** The skill's identity is framed around its own capability, not around another skill as its consumer.

## Subagent prompts

Workers in `subagents/` are invoked by composing the canonical worker contract from the `worker-contract` skill with the `write-a-skill`-specific composition layer in `subagents/_TEMPLATE.md` and the role-specific instructions in the worker file. The template adds the common return format, forbidden actions, and default tool/scope boundaries used by this conductor; see `references/WORKER_CONTRACT.md` for the shared contract and addendum.

Workers:

- [map-objective.md](subagents/map-objective.md) — build and confirm the objective map with the user.
- [classify-intent.md](subagents/classify-intent.md) — classify the user's request into a top-level branch.
- [classify-skill-type.md](subagents/classify-skill-type.md) — classify the skill type.
- [suggest-patterns.md](subagents/suggest-patterns.md) — suggest patterns.
- [check-chainlog-needs.md](subagents/check-chainlog-needs.md) — evaluate whether the skill should produce, consume, or both chainlog observations.
- [initialize.md](subagents/initialize.md) — first-run configuration proposal.
- [draft-skill-md.md](subagents/draft-skill-md.md) — draft the `SKILL.md` file.
- [change-branch.md](subagents/change-branch.md) — coordinate the `change` branch by resolving `standards_path` and invoking `review-skill`.

## Create branch

**Why this branch exists:** building the wrong skill is expensive, and a structured design process prevents scope creep, hidden assumptions, and bloated drafts before any files are written. The branch also handles the "what should I build?" question.

**Internal gates**

| Gate       | Trigger                                                                                            | Outcome                                  | Completion criterion                                                                                                                                           |
| ---------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **full**   | User wants a complete design from scratch.                                                         | Full design workflow + draft.            | A final review report exists in `{context}/skill-design/{skill-name}-design.md` and the user has explicitly approved, requested changes, or closed the branch. |
| **quick**  | User wants a minimal skill from a brief description.                                               | Compressed design workflow + draft.      | A final review report exists in `{context}/skill-design/{skill-name}-design.md` and the user has explicitly approved, requested changes, or closed the branch. |

Shape uncertainty ("is a skill even the right answer?") is handled by the `explore` branch, which delegates to `decide-skill-shape`. For the full phase list per gate, see [references/BRANCH_WORKFLOWS.md][branch-workflows].

## Change branch

**Why this branch exists:** Skills drift and accumulate bloat. The change branch audits an existing skill by applying the review principles from `{standards_path}/reference/review-principles.md`, then produces a verdict-led report or incomplete report. The conductor invokes `review-skill` as a subagent through [subagents](subagents/change-branch.md); it does not perform inline reviews. Before scoring, the conductor rebuilds the target skill's objective map and confirms the comprehension brief with the user — scoring never starts on an unconfirmed understanding.

**Internal gates**

| Gate       | Trigger                                                                   | Outcome                                                                | Completion criterion                                                                                                      |
| ---------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **review** | User wants to audit an existing skill without changing it.                | Verdict-led audit report, or incomplete report.                        | The audit report is complete, includes a verdict supported by findings, and references the rubric criteria by id.         |
| **update** | User wants to refine or polish an existing skill to follow the standards. | Verdict-led audit report → remediation plan → draft changes → confirm. | A verdict-led audit report exists, a remediation plan exists, and the user has approved or declined each proposed change. |

### Change branch workflow

The conductor invokes `subagents/change-branch.md` to coordinate the following pipeline. Each phase ends with a completion criterion.

| Phase                                    | What happens                                                                 | Completion criterion                                                             |
| ---------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 1. **Resolve standards path**            | Load `standards_path` from config or detect it from project-context markers. | `standards_path` is resolved and recorded as canonical, degraded, or missing.    |
| 2. **Load target skill**                 | Read `SKILL.md`, `README.md`, references, subagents, scripts, and assets.    | All target skill files are loaded.                                               |
| 3. **Classify gate**                     | Map user intent to `review` or `update`.                                     | Gate is one of {review, update} and user confirmed.                              |
| 4. **Invoke `review-skill`**             | Delegate to `review-skill` with the target skill and `standards_path`.       | `review-skill` returns a comprehension brief, audit report, or remediation plan. |
| 5. **Confirm comprehension** | Present the rebuilt objective map and the `review-skill` comprehension brief; the user confirms or corrects it. | User confirmed understanding; scoring has not started. |
| 6. **Produce incomplete report**         | If core questions cannot be answered, stop and record open questions.        | Incomplete report exists; no verdict is issued.                                  |
| 7. **Run `audit-skill`**                 | Evaluate the target skill against the fundamentals rubric.                   | Audit report exists with findings.                                               |
| 8. **Run `validate-skill-frontmatter`**  | Check frontmatter schema compliance.                                         | Validation result is captured.                                                   |
| 9. **Produce verdict-led report**        | Lead with a verdict, then findings and recommendations.                      | For `review`, the audit report is complete.                                      |
| 10. **Produce remediation plan (update)** | List concrete changes with rationale and effort.                             | For `update`, a remediation plan exists.                                         |
| 11. **Confirm and apply (update)**       | Present the plan; apply approved changes; run final audit.                   | Approved changes applied; final audit report exists.                             |

For the full phase list per gate, including the `change` branch delegation to `review-skill`, see [references/BRANCH_WORKFLOWS.md][branch-workflows].

## Initialization

On first run in a project, or when the user asks to reconfigure, execute the `initialize` branch. The conductor uses the `subagents/initialize` worker and the `scripts/initialize-config.py` script to propose, confirm, and persist configuration.

1. Detect project context with `detect-project-context` to locate the project root and the recommended config directory.
2. Load config from `{recommended_config_dir}/write-a-skill.yaml` or create defaults.
3. Invoke `subagents/initialize.md` to propose:
   - `config_dir`: where to write `write-a-skill.yaml`.
   - `context_dir`: where context reports are written.
   - `standards_path`: path to the canonical skill standards directory.
   - `capability_index_path`: path to the machine-readable capability index (defaults to the project-local override and bundle defaults).
   - `registries`: list of skill registries to search.
4. Report whether the canonical standards are found locally, missing, or need fetching.
5. If standards are missing, offer to fetch only the canonical skill standards directory from [skills](https://github.com/wianvdm/skills). Show the user the exact source (repository, ref or commit, and directory) before downloading. Every fetch must be explicitly confirmed by the user. Record the fetched ref in the persisted config so later drift checks can freshness-date the copy.
6. If the user declines or the fetch fails, warn with the degraded-mode template from [references/PLUGGABILITY.md][pluggability] and fall back to embedded [references/FUNDAMENTALS.md][fundamentals] and [references/PATTERN_HINTS.md][pattern-hints].
7. Ask the user to confirm detected paths, default registry list, and standards source.
8. Only after explicit approval, run `scripts/initialize-config.py` to write `write-a-skill.yaml`.
9. Persist initial notes in the context directory.

If the project context cannot be detected, fail closed and explain what is missing.

### Standards availability

Every branch that reads canonical standards must check `standards_path` before use:

- If `standards_path` points to an existing directory, use it.
- If the directory is missing or the value is unset, use the degraded-mode template from [references/PLUGGABILITY.md][pluggability] to warn the user that some checks are unavailable.
- Prefer the shared resolver `skills/blocks/project/detect-project-context/scripts/resolve-standards-path.py` instead of reimplementing the resolution order.
- Record the user's choice in the decision log.
- Never silently fall back to embedded docs without telling the user.

## State and artifacts

All artifacts are written as context reports so the session can survive compaction and be resumed. For shared context-report conventions, see the `context-reports` skill. Paths are relative to the detected context directory.

| Artifact            | Location                                                       | Purpose                                                                              |
| ------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Intent note         | `{context}/skill-design/{skill-name}-intent.md`                | Captured user intent, constraints, and chosen branch/gate.                           |
| Alternatives report | `{context}/skill-design/{skill-name}-alternatives.md`          | Existing skills and third-party options found.                                     |
| Overlap findings    | `{context}/skill-design/{skill-name}-overlap-findings.md`      | Score-ranked overlap findings and extraction candidates from `detect-skill-overlap`. |
| Design draft        | `{context}/skill-design/{skill-name}-design.md`                | Structured design: identity, scope, type, patterns, dependencies.                    |
| Self-audit report   | `{context}/skill-review/{skill-name}-self-audit.md`            | Fundamentals check results.                                                        |
| Decision log        | `{context}/skill-design/{skill-name}-decisions.md`             | Append-only record of decisions and rationale.                                     |

Append decisions rather than overwriting them. Never overwrite an existing file without asking.

## Resumption logic

If the conversation is compacted, resume by reading the latest state files in this order:

1. Decision log.
2. Intent note.
3. Overlap findings report (to understand prior reuse/colocate/extract decisions).
4. Design draft or review report (whichever is most recent).
5. Latest self-audit or audit report.

Summarize completed work, pending work, current focus, and the recommended next action before continuing.

## User interaction rules

- **Ask one question at a time** when the answer shapes later decisions.
- **Present recommendations, not just options.** Propose a default and explain why.
- **Confirm before any destructive action.** Writing, overwriting, or installing requires explicit approval.
- **Pair every negation with a positive directive.** For example: _Confirm the design before drafting; do not draft until the design is confirmed._
- **Block on principle violations.** Explain the principle, why it matters, and offer a concrete alternative.
- **Warn on preference choices.** Explain the trade-off and recommend a default.
- **Ask when detection is ambiguous.** Present detected options and let the user choose.
- **In an untrusted project, prefer read-only inspection.** Confirm before reading skill files from a project you do not trust.

## Dependencies

`write-a-skill` delegates deterministic work to standalone building-block skills and uses subagents only for tightly coupled design judgment. The dependency taxonomy follows `{standards_path}/fundamentals/architecture/dependencies-and-bundling.md`:

- **Required** — the skill cannot function without this dependency.
- **Recommended** — improves output or experience; the skill runs degraded if it is missing.
- **Optional** — only needed for a side branch or advanced feature.

See [references/DEPENDENCIES.md][dependencies] for the full classified dependency list, required capabilities, binaries, and consumed references.

The frontmatter of this skill also declares a `depends` field for harness auto-installation.

## Security

- **No secret handling.** `write-a-skill` does not read secrets, tokens, or credentials directly. Any drafted skill that needs a secret should use the `token-resolver` building block when available; otherwise it references the required environment variable by name. It must never read or store secret values itself.
- **Explicit fetch.** The initializer may fetch canonical skill standards from a public repository only after explicit user approval.
- **No silent writes.** No drafted skill is written without explicit user approval.
- **Degraded disclosure.** The conductor must warn users when a degraded source (e.g., embedded fundamentals instead of canonical standards) is used and record the consent.
- **Subagent boundaries.** Subagents are forbidden from executing destructive actions or asking users directly.
- **Untrusted projects.** In an untrusted project, prefer read-only inspection and confirm before reading or writing skill files.

## References

- [Objective map][objective-map]
- [Fundamentals (condensed)][fundamentals]
- [Pattern hints (condensed)][pattern-hints]
- [Pluggability and detection][pluggability]
- [Branch workflows][branch-workflows]
- [Worker return contract][worker-contract]
- [Integration test interfaces][integration-tests]
- [Composition test][composition-test]
- [State and artifact schemas][state-schema]

[objective-map]: references/OBJECTIVE_MAP.md
[fundamentals]: references/FUNDAMENTALS.md
[pattern-hints]: references/PATTERN_HINTS.md
[pluggability]: references/PLUGGABILITY.md
[branch-workflows]: references/BRANCH_WORKFLOWS.md
[dependencies]: references/DEPENDENCIES.md
[worker-contract]: references/WORKER_CONTRACT.md
[integration-tests]: references/INTEGRATION_TESTS.md
[composition-test]: references/COMPOSITION_TEST.md
[state-schema]: references/STATE_SCHEMA.md
