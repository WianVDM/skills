---
name: write-a-skill
description: Design, review, and update skills that follow the skill standards. Coordinates creation, audit, remediation, and first-run initialization.
version: 1.0.1
invocation: user-invoked
depends:
  - detect-project-context
  - decide-skill-shape
  - audit-skill
  - validate-skill-frontmatter
  - review-skill
  - eval-format
  - worker-contract
  - context-reports
  - parse-skill-frontmatter
  - list-available-skills
  - search-skills-registry
  - detect-skill-overlap
  - install-skill
  - run-trigger-evals
  - prototype
---

# write-a-skill

## Purpose

Help the user produce a skill that satisfies the skill fundamentals and applies the right architecture patterns.

## In scope

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
- **No hardcoded project paths:** paths are resolved through detection, configuration, or user confirmation.
- **Self-contained:** the skill ships with condensed fundamentals in [references/FUNDAMENTALS.md][fundamentals] and [references/PATTERN_HINTS.md][pattern-hints]. It can optionally bootstrap the full standards from a public repository on first run.

## Branch entry

Classify the user's intent into one top-level branch. If the intent is unclear, ask one clarifying question with a proposed default.

| Branch         | Trigger                                                                 | Internal gate                | Outcome                                                                   |
| -------------- | ----------------------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------- |
| **initialize** | No `write-a-skill.yaml` config exists, or the user asks to reconfigure. | `config`                     | A persisted `write-a-skill.yaml` with project paths and standards source. |
| **create**     | User wants to produce a new skill or is unsure what shape to build.     | `full`, `quick`, or `decide` | A designed and audited new skill, or a recommendation report.             |
| **change**     | User wants to audit or refine an existing skill.                        | `review` or `update`         | An audit report, or a remediation plan with optional changes.             |

**Completion criterion:** the branch is one of {create, change, initialize} and the user has confirmed or corrected the default.

## Workflow

The conductor runs this pipeline. Each phase has a completion criterion and a decision gate. Phases may be compressed for the `quick` gate and skipped for the `decide` gate.

| Phase                                      | What happens                                                                                                                                                                                                                                | Completion criterion                                                                                                     |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 1. **Clarify intent and choose gate**      | Classify the top-level branch; resolve the internal gate; ask one question at a time if unclear.                                                                                                                                            | Branch is one of {create, change, initialize}, gate is resolved, and user confirmed.                                     |
| 2. **Explore alternatives**                | Use `list-available-skills`, `search-skills-registry`, and `detect-skill-overlap` to see what exists and flag overlap with existing skills.                                                                                                 | Alternatives report exists; overlap scan is complete; user knows whether to create, reuse, or install.                   |
| 3. **Decide shape and colocation**         | Decide whether the answer is a new skill, an existing skill, a script, an MCP server, or a context file. Then apply the colocation principle and invoke `detect-skill-overlap` to flag extraction opportunities or unjustified duplication. | User confirms the chosen shape and that extraction is justified, or agrees to colocate.                                  |
| 4. **Define identity**                     | Name, description, invocation. Version only if the user requires it or the skill will be shared/consumed.                                                                                                                                   | Frontmatter skeleton exists and user confirmed.                                                                          |
| 5. **Define scope**                        | In-scope, out-of-scope, branches, assumptions.                                                                                                                                                                                              | Scope boundaries are explicit and defensible.                                                                            |
| 6. **Select patterns**                     | Apply fundamentals; suggest Layer 2 patterns. Decide if the skill is configurable and, if so, which shared and skill-specific keys it needs.                                                                                                | Pattern list and config declaration (if any) exist and user confirmed.                                                   |
| 6a. **Pattern adherence**                  | Compare the chosen patterns against the canonical skill-standards docs; flag deviations before drafting.                                                                                                                                    | Pattern list is explicitly mapped to canonical pattern documents; deviations are recorded with rationale.                |
| 6b. **Design capability-to-tool strategy** | For each load-bearing capability, identify the preferred tool, fallback tools, and degraded-output disclosure. Document the selection rule and user-consent behavior.                                                                       | A capability-to-tool mapping exists for every load-bearing capability; the user has confirmed or corrected the strategy. |
| 7. **Token justification**                 | Defend every proposed section, reference, subagent, and script; remove or merge unjustified items.                                                                                                                                          | Every artifact in the draft has a stated purpose; the user has confirmed the minimal set.                                |
| 8. **Draft artifacts**                     | Generate `SKILL.md`, optional `README.md`, `references/`, `subagents/`, `scripts/`, `assets/`, and `config.yaml` if the skill is configurable.                                                                                              | Draft files exist and are linked correctly.                                                                              |
| 9. **Audit and validate**                  | Run `audit-skill` and `validate-skill-frontmatter`.                                                                                                                                                                                         | Audit report exists with no blocking failures.                                                                           |
| 10. **Generate evals**                     | Run `run-trigger-evals` for model-invoked skills.                                                                                                                                                                                           | `evals/evals.json` exists or user declined.                                                                              |
| 11. **Confirm and write**                  | Present the full plan; write files only after explicit approval.                                                                                                                                                                            | User approved; files written; decision log updated.                                                                      |

## Tooling-awareness design checklist

This checklist is load-bearing. The conductor must confirm each applicable item explicitly with the user before moving to the Draft phase. If an item does not apply, record the rationale in the decision log.

- **Outcome first.** Every load-bearing capability step names the outcome before choosing a tool.
- **Tool discovery.** The skill detects available tools across all categories (skill adapters, MCP servers, native binaries, direct APIs, harness tools, manual fallback).
- **Best available tool.** The skill prefers the best available tool, not just the adapter it ships with.
- **Documented selection.** The preferred tool, fallback tools, and selection rule are documented.
- **Degraded disclosure.** If a degraded source is used, the skill tells the user what better option was available and gets explicit or recorded consent.
- **Dependency surface.** The full dependency surface is declared in `references/DEPENDENCIES.md` and `skills.json`.

## Colocation and extraction checklist

Before deciding a new skill is needed, the conductor must confirm:

- **Reuse justification.** The capability is used by more than one skill, or is a cross-cutting concern, or has a stable narrow interface, or solves a generic-domain problem.
- **No speculative extraction.** The capability is not being extracted only because it is "self-contained" or "might be useful someday."
- **Single-consumer warning.** If the capability is only used by one existing skill, the user has explicitly agreed that a separate skill is justified.
- **Identity framing.** The skill's identity is framed around its own capability, not around another skill as its consumer.

## Subagent prompts

Workers in `subagents/` are invoked by composing the canonical worker contract from the `worker-contract` skill with the `write-a-skill`-specific composition layer in `subagents/_TEMPLATE.md` and the role-specific instructions in the worker file. The template adds the common return format, forbidden actions, and default tool/scope boundaries used by this conductor; see `references/WORKER_CONTRACT.md` for the shared contract and addendum.

## Create branch

**Why this branch exists:** building the wrong skill is expensive, and a structured design process prevents scope creep, hidden assumptions, and bloated drafts before any files are written. The branch also handles the "what should I build?" question.

**Internal gates**

| Gate       | Trigger                                                                                            | Outcome                                  | Completion criterion                                                                                                                                           |
| ---------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **full**   | User wants a complete design from scratch.                                                         | Full design workflow + draft.            | A final review report exists in `{context}/skill-design/{skill-name}-design.md` and the user has explicitly approved, requested changes, or closed the branch. |
| **quick**  | User wants a minimal skill from a brief description.                                               | Compressed design workflow + draft.      | A final review report exists in `{context}/skill-design/{skill-name}-design.md` and the user has explicitly approved, requested changes, or closed the branch. |
| **decide** | User is unsure whether the answer should be a skill, script, MCP, context file, or existing skill. | Recommendation report; no files written. | A decision report exists and the user has confirmed or rejected the recommended next step, or asked for more options.                                          |

For the full phase list per gate, including the `decide` gate delegation to `decide-skill-shape`, see [references/BRANCH_WORKFLOWS.md][branch-workflows].

## Change branch

**Why this branch exists:** Skills drift and accumulate bloat. The change branch audits an existing skill by applying the review principles from `docs/skill-standards/reference/review-principles.md`, then produces a verdict-led report or incomplete report.

**Internal gates**

| Gate       | Trigger                                                                   | Outcome                                                                | Completion criterion                                                                                                      |
| ---------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **review** | User wants to audit an existing skill without changing it.                | Verdict-led audit report, or incomplete report.                        | The audit report is complete, includes a verdict supported by findings, and references the rubric criteria by id.         |
| **update** | User wants to refine or polish an existing skill to follow the standards. | Verdict-led audit report → remediation plan → draft changes → confirm. | A verdict-led audit report exists, a remediation plan exists, and the user has approved or declined each proposed change. |

For the full phase list per gate, including the `change` branch delegation to `review-skill`, see [references/BRANCH_WORKFLOWS.md][branch-workflows].

## Initialization

On first run in a project, or when the user asks to reconfigure, execute the `initialize` branch. The conductor uses the `subagents/initialize` worker and the `scripts/initialize-config.py` script to propose, confirm, and persist configuration.

1. Detect project context with `detect-project-context` to locate the project root and the recommended config directory.
2. Load config from `{recommended_config_dir}/write-a-skill.yaml` or create defaults.
3. Invoke `subagents/initialize.md` to propose:
   - `config_dir`: where to write `write-a-skill.yaml`.
   - `context_dir`: where context reports are written.
   - `standards_path`: path to the canonical `docs/skill-standards/` directory.
   - `registries`: list of skill registries to search.
4. Report whether the canonical standards are found locally, missing, or need fetching.
5. If standards are missing, offer to fetch only the `docs/skill-standards/` directory from `github.com/wianvdm/skills`. Every fetch must be explicitly confirmed by the user.
6. If the user declines or the fetch fails, warn with the degraded-mode template from [references/PLUGGABILITY.md][pluggability] and fall back to embedded [references/FUNDAMENTALS.md][fundamentals] and [references/PATTERN_HINTS.md][pattern-hints].
7. Ask the user to confirm detected paths, default registry list, and standards source.
8. Only after explicit approval, run `scripts/initialize-config.py` to write `write-a-skill.yaml`.
9. Persist initial notes in the context directory.

If the project context cannot be detected, fail closed and explain what is missing.

### Standards availability

Every branch that reads canonical standards must check `standards_path` before use:

- If `standards_path` points to an existing directory, use it.
- If the directory is missing or the value is unset, use the degraded-mode template from [references/PLUGGABILITY.md][pluggability] to warn the user that some checks are unavailable.
- Record the user's choice in the decision log.
- Never silently fall back to embedded docs without telling the user.

## State and artifacts

All artifacts are written as context reports so the session can survive compaction and be resumed. For shared context-report conventions, see the `context-reports` skill. Paths are relative to the detected context directory.

| Artifact            | Location                                              | Purpose                                                           |
| ------------------- | ----------------------------------------------------- | ----------------------------------------------------------------- |
| Intent note         | `{context}/skill-design/{skill-name}-intent.md`       | Captured user intent, constraints, and chosen branch/gate.        |
| Alternatives report | `{context}/skill-design/{skill-name}-alternatives.md` | Existing skills and third-party options found.                    |
| Design draft        | `{context}/skill-design/{skill-name}-design.md`       | Structured design: identity, scope, type, patterns, dependencies. |
| Self-audit report   | `{context}/skill-review/{skill-name}-self-audit.md`   | Fundamentals check results.                                       |
| Decision log        | `{context}/skill-design/{skill-name}-decisions.md`    | Append-only record of decisions and rationale.                    |

Append decisions rather than overwriting them. Never overwrite an existing file without asking.

## Resumption logic

If the conversation is compacted, resume by reading the latest state files in this order:

1. Decision log.
2. Intent note.
3. Design draft or review report (whichever is most recent).
4. Latest self-audit or audit report.

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

`write-a-skill` delegates deterministic work to standalone building-block skills and uses subagents only for tightly coupled design judgment. The dependency taxonomy follows `docs/skill-standards/fundamentals/architecture/dependencies-and-bundling.md`:

- **Required** — the skill cannot function without this dependency.
- **Recommended** — improves output or experience; the skill runs degraded if it is missing.
- **Optional** — only needed for a side branch or advanced feature.

Dependencies are not limited to other skills. The skills drafted by this conductor may depend on any of the following tool categories:

| Category                | Examples                                                   |
| ----------------------- | ---------------------------------------------------------- |
| **Provider-specific adapters** | GitHub PR adapter, SonarCloud adapter, Jira adapter |
| **MCP tools / servers** | `github_get_pull_request_reviews`, SonarQube MCP, Jira MCP |
| **Native binaries**     | `gh`, `git`, `curl`, `jq`                                  |
| **Direct APIs**         | Provider REST or GraphQL endpoints                         |
| **Harness tools**       | Built-in browser, file system, search, shell               |
| **Manual fallback**     | User input, CSV, markdown files                            |

The conductor must teach authors to design capability-first: identify the needed outcome, discover available tools across categories, select the best one, and disclose the choice.

### Required skills

- **detect-project-context** — project root, skills dir, context dir, and config dir detection.
- **decide-skill-shape** — recommend whether a problem should be a new skill, script, MCP, context file, or mode.
- **audit-skill** — evaluate a skill against the fundamentals rubric.
- **validate-skill-frontmatter** — validate `SKILL.md` frontmatter against the JSON schema.
- **review-skill** — audit an existing skill and optionally apply remediation changes.
- **eval-format** — shared `evals/evals.json` schema and evaluation conventions.
- **worker-contract** — shared subagent return contract, forbidden actions, and scope boundaries used when composing worker prompts.
- **context-reports** — shared context-report conventions, schema, freshness rules, and missing-report handling.
- **parse-skill-frontmatter** — extract canonical frontmatter fields from a `SKILL.md` file (used by several building blocks above).

### Recommended skills

- **list-available-skills** — discover skills already available in the project and user scope. Without it, the alternatives report is limited to what the conductor can find directly.
- **search-skills-registry** — find third-party skills in configured registries. Without it, the skill cannot check whether a similar third-party skill already exists.
- **install-skill** — install a skill from a local path or archive URL after confirmation. Without it, the conductor can draft files but cannot install skills on the user's behalf.
- **run-trigger-evals** — generate `evals/evals.json` for model-invoked skills. Without it, the conductor can ask the user to write evals manually or skip them.

### Optional skills

- **prototype** — only used when the user explicitly asks to prototype a UI variation before drafting a skill. Not on the main path.

See [references/DEPENDENCIES.md][dependencies] for the full classified dependency list, required capabilities, binaries, and consumed references.

The frontmatter of this skill also declares a `depends` field for Vercel CLI auto-installation.

Required capabilities: file read, file write, file edit, directory listing, script execution, and search. Required binary: Python 3.x for bundled scripts.

## Security

- **No secret handling.** `write-a-skill` does not read secrets, tokens, or credentials directly. Any drafted skill that needs a secret must use the `token-resolver` building block or equivalent and must not read environment variables or files containing credentials itself.
- **Explicit fetch.** The initializer may fetch canonical skill standards from a public repository only after explicit user approval.
- **No silent writes.** No drafted skill is written without explicit user approval.
- **Degraded disclosure.** The conductor must warn users when a degraded source (e.g., embedded fundamentals instead of canonical standards) is used and record the consent.
- **Subagent boundaries.** Subagents are forbidden from executing destructive actions or asking users directly.
- **Untrusted projects.** In an untrusted project, prefer read-only inspection and confirm before reading or writing skill files.

## References

- [Fundamentals (condensed)][fundamentals]
- [Pattern hints (condensed)][pattern-hints]
- [Pluggability and detection][pluggability]
- [Branch workflows][branch-workflows]
- [Worker return contract][worker-contract]
- [Integration test interfaces][integration-tests]
- [Composition test][composition-test]
- [State and artifact schemas][state-schema]

[fundamentals]: references/FUNDAMENTALS.md
[pattern-hints]: references/PATTERN_HINTS.md
[pluggability]: references/PLUGGABILITY.md
[branch-workflows]: references/BRANCH_WORKFLOWS.md
[dependencies]: references/DEPENDENCIES.md
[worker-contract]: references/WORKER_CONTRACT.md
[integration-tests]: references/INTEGRATION_TESTS.md
[composition-test]: references/COMPOSITION_TEST.md
[state-schema]: references/STATE_SCHEMA.md
