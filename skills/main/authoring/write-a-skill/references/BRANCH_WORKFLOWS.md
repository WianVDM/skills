# Branch workflows

This reference holds the detailed step-by-step workflows for each `write-a-skill` internal gate. `SKILL.md` keeps the top-level branch summary and completion criterion; reach this file when the conductor needs the full phase list for a gate.

Top-level branches:

- **Create branch** — for producing a new skill or deciding what shape to build. Internal gates: `full`, `quick`, `decide`.
- **Change branch** — for auditing or updating an existing skill. Internal gates: `review`, `update`.

## Conventions

- Every branch starts at **phase 0: objective map** (see [OBJECTIVE_MAP.md][objective-map]). Nothing downstream runs on an unconfirmed map.
- Each phase ends with a **completion criterion**.
- The conductor does not advance to the next phase until the criterion is met or the user explicitly overrides it.
- Destructive actions (writing, overwriting, installing) always require explicit approval.

## Initialize branch

The `initialize` branch runs on first run or when the user asks to reconfigure `write-a-skill`. It does not write skill files; it only produces and persists the `write-a-skill.yaml` configuration file.

### 1. Detect project context

Use `detect-project-context` to locate the project root, skills directory, context directory, and recommended config directory.

**Completion criterion:** the detected paths and confidence level are recorded in the initializer proposal.

### 2. Propose config

Invoke the `subagents/initialize` worker with the detected project context. It returns a proposed config containing:

- `config_dir`: where to write `write-a-skill.yaml`.
- `context_dir`: where context reports are written.
- `standards_path`: path to the canonical skill standards directory.
- `capability_index_path`: path to the machine-readable capability index (project-local override or bundle default).
- `registries`: list of skill registries to search.

**Completion criterion:** a config proposal exists and the worker has reported standards availability (`found`, `missing`, or `incomplete`).

### 3. Resolve standards source

- If `standards_path` points to an existing directory with expected files, use it.
- If the directory is missing or incomplete, offer to fetch only the canonical skill standards directory from `github.com/wianvdm/skills`. Show the user the exact source (repository, ref or commit, and directory) before downloading; record the fetched ref in the persisted config for later drift checks.
- If the user declines or the fetch fails, use the degraded-mode warning template from [PLUGGABILITY.md][pluggability] and fall back to embedded fundamentals and pattern hints.

**Completion criterion:** the standards source is confirmed by the user and the degraded-mode warning (if any) is recorded.

### 4. Confirm and write

Ask the user to confirm each proposed value. Only after explicit approval, run `scripts/initialize-config.py --approve` to write `write-a-skill.yaml`.

**Completion criterion:** `write-a-skill.yaml` exists at the confirmed path and the user has acknowledged the next steps.

[pluggability]: PLUGGABILITY.md

## Create branch

### Create branch — full gate

This is the full design workflow for a new skill from scratch.

#### 0. Objective map

**Why:** designing the wrong skill is expensive. The objective map is the confirmed foundation every later phase reads from.

Build the objective map with the user via the `map-objective` worker: prefill the nine fields from the request, present the whole map, and grill only the gaps. See [OBJECTIVE_MAP.md][objective-map] for the fields and protocol.

**Completion criterion:** the map is confirmed by the user and persisted to the intent note.

#### 1. Explore alternatives

**Why:** a new skill should be the last resort, not the first.

Run `list-available-skills`, `search-skills-registry`, and `detect-skill-overlap` to find existing skills, scripts, MCP servers, or context files that might cover the problem.

For any candidate that looks similar, run `detect-skill-overlap` against the proposed skill directory or a JSON draft. The script produces a structured report with:

- Score-ranked overlap findings against existing skills.
- Extraction candidates with interface sketches and effort estimates.
- Warnings when the capability index is stale or missing.

Write the report to `{context}/skill-design/{skill-name}-overlap-findings.md` and present the top findings to the user. Do not make a decision yet; this phase only surfaces evidence.

**Completion criterion:** the alternatives report lists existing options, the overlap findings report exists, and the user knows whether to build new, reuse/extend existing, or install.

#### 2. Decide shape and colocation

**Why:** the shape of the solution determines every later decision, and whether the capability should live inside an existing skill determines whether a new skill is warranted at all.

Confirm with the user that a new skill is the right shape, not a script, MCP server, context file, or installed skill. Then apply the colocation principle and invoke `detect-skill-overlap` to flag extraction opportunities or unjustified duplication: if the capability is only used by one existing skill, recommend colocating it inside that skill unless extraction is justified by reuse (cross-cutting concern, multiple current consumers, stable narrow interface, or generic-domain problem).

For each significant overlap in the overlap findings report, present the user with three options:

- **Reuse** — use the existing skill instead of building a new one.
- **Colocate** — keep the capability in the new skill because the context is different.
- **Extract** — create a new building block and have both skills depend on it.

Record the user's choice in `{context}/skill-design/{skill-name}-decisions.md`. For each extraction candidate, include the capability name, category, other skills that implement it, the suggested interface sketch, and the **capability contract skeleton** (a draft `SKILL.md` for the proposed building block) from the overlap findings report.

**Completion criterion:** the user confirms the chosen shape is a new skill and the reuse/colocate/extract decision for each significant overlap; any extraction candidates have interface sketches and a recorded rationale.

#### 3. Define identity

**Why:** a confirmed identity is the contract that prevents scope creep and naming drift.

Produce a frontmatter skeleton: name, description, invocation. Add harness hints such as `depends` only if the target harness requires them.

**Completion criterion:** the design draft contains an identity section and the user has confirmed it.

#### 4. Define scope

**Why:** clear boundaries prevent bloat and hidden assumptions.

Write one core objective, explicit in-scope items, and explicit out-of-scope items.

**Completion criterion:** the scope boundaries are explicit and do not contradict each other.

#### 5. Description design

**Why:** the description is the routing surface — the most important field in `SKILL.md`. It is designed, not filled in.

Draft the description from the objective map: leading word or domain first, one trigger per distinct branch from the map's triggers field, a reach clause if other skills consume the skill, ≤ 1024 characters. Present it to the user for confirmation before any drafting begins.

**Completion criterion:** the description follows the canonical shape and the user has confirmed it.

#### 6. Select patterns

**Why:** applying the right patterns makes the skill portable, maintainable, and composable.

Apply the fundamentals from [references/FUNDAMENTALS.md][fundamentals] and select Layer 2 patterns using [PATTERN_HINTS.md][pattern-hints]. Decide if the skill is configurable and, if so, which shared and skill-specific keys it needs. For each pattern, cite the canonical document from the `standards_path` if available; otherwise, note the degraded source and warn the user.

**Completion criterion:** the pattern list exists, each pattern is mapped to a canonical source or marked as degraded, and the user has confirmed it.

#### 6a. Pattern adherence

**Why:** patterns are not optional styling; deviations must be justified and recorded before drafting.

Compare the selected patterns against the canonical skill-standards docs. For each pattern, confirm one of:

- The skill follows the canonical guidance.
- The deviation is justified and recorded in the decision log.
- The canonical docs are unavailable and the skill falls back to embedded guidance with a degraded-mode warning.

**Completion criterion:** the pattern list is explicitly mapped to canonical pattern documents; deviations are recorded with rationale; the user has confirmed.

#### 6b. Design capability-to-tool strategy

**Why:** designing the capability-to-tool strategy up front prevents adapter tunnel vision.

For each load-bearing capability, build a capability matrix (preferred tool, fallback tools, degraded-output disclosure, user-consent behavior) using the guidance in [PATTERN_HINTS.md][pattern-hints]. For dependencies, decide:

- Which are **required** and must be checked at initialization.
- Which are **recommended** or **optional** and can be evaluated **lazily** when the relevant method or branch is selected.

Document the lazy evaluation strategy and the capability-to-tool matrix in the design draft so the drafted skill does not ask the user to configure unrelated tooling upfront.

**Completion criterion:** the capability-to-tool matrix covers every load-bearing capability, the dependency evaluation strategy is documented, and the user has confirmed it.

#### 7. Token justification

**Why:** every section, reference, subagent, and script consumes tokens and maintenance burden. Unjustified artifacts are bloat.

Before drafting, defend every proposed artifact. For each item, answer: *What behavior does this change? What would break if it were removed?* Merge or remove items that cannot be defended. If a proposed reference duplicates a shared convention (e.g., context-report envelope, eval format), point to the canonical source instead of copying it.

**Completion criterion:** every artifact in the draft has a stated purpose; the user has confirmed the minimal set; the conductor has recorded any retained-but-questionable items with rationale.

#### 8. Draft artifacts

**Why:** only after the design is approved does the skill produce concrete files. Drafting is the execution of the design, not the design itself.

Generate `SKILL.md`, optional `README.md`, references, subagents, scripts, and assets/templates.

**Completion criterion:** all files in the approved design are created and the directory structure matches the design.

#### 9. Audit and validate

**Why:** the design may pass, but the drafted files can still drift.

Run `audit-skill` and `validate-skill-frontmatter`. Fix blockers before showing the result to the user.

**Completion criterion:** the audit report exists with no blocking failures, or the user has explicitly recorded a reason for overriding a blocker.

#### 10. Generate evals

**Why:** model-invoked skills need trigger evals to be testable and reliable.

Run `run-trigger-evals` for model-invoked skills. If the user declines, record the decision in the decision log.

**Completion criterion:** `evals/evals.json` exists or the user has explicitly declined.

#### 11. Confirm and write

**Why:** drafting files without approval is the most common destructive action in this skill.

Present the design, audit, and alternatives summary. Write files only after explicit approval.

**Completion criterion:** the user has explicitly approved the design and files are written.

### Create branch — quick gate

A compressed version of the full gate for minimal skills.

1. **Objective map** (minimal) — prefill the nine fields from the brief, confirm with the user.
2. **Explore alternatives** (light) — check existing skills and simple alternatives; run `detect-skill-overlap` for any close match and write the findings to `{context}/skill-design/{skill-name}-overlap-findings.md`.
3. **Decide shape and colocation** — name and invocation; decide whether to colocate inside an existing skill or extract as a new reusable skill; invoke `detect-skill-overlap` to flag extraction opportunities; present the user with reuse/colocate/extract options and record decisions in the decision log.
4. **Define scope** — one objective, in-scope, out-of-scope.
5. **Description design** — leading word, distinct triggers, reach clause, ≤ 1024 characters, confirmed.
6. **Select patterns** — apply fundamentals.
7. **Pattern adherence** — confirm pattern mappings or deviations; warn if canonical docs are unavailable.
8. **Token justification** — defend the minimal artifact set; remove duplicates.
9. **Design capability-to-tool strategy** — for each load-bearing capability, note the preferred tool, fallback, and degraded-output disclosure.
10. **Draft** — write the skill files.
11. **Audit** — run `audit-skill` and `validate-skill-frontmatter`.
12. **Confirm and write** — get approval before writing.

## Explore branch

The entry point for vague ideas and rough drafts. The output is a confirmed objective map and a recommendation — never files.

### 1. Objective map

Build the map with the user via `map-objective` (prefill-and-confirm; grill the gaps). See [OBJECTIVE_MAP.md][objective-map].

**Completion criterion:** the map is confirmed and persisted to the intent note.

### 2. Explore what exists

Run `list-available-skills`, `search-skills-registry`, and `detect-skill-overlap`. Write overlap findings to `{context}/skill-design/{skill-name}-overlap-findings.md`.

**Completion criterion:** the alternatives report exists and the user has seen the top findings.

### 3. Resolve the shape (if unclear)

If the open question is shape — skill, script, MCP server, context file, or existing skill — invoke `decide-skill-shape` and consume its decision report. Do not leave the branch.

**Completion criterion:** the shape is confirmed, or the user accepts a recommendation to revisit later.

### 4. Recommend

Present one of four outcomes with reasoning:

- **Build it** — hand the confirmed map to the `create` branch.
- **Reuse or extend** — name the existing skill and show the fit.
- **Simpler answer** — a script, MCP server, context file, or rule.
- **Not worth it** — record why; nothing is written.

**Completion criterion:** the user has confirmed the recommendation; no files were written.

## Change branch

The `change` branch audits or updates an existing skill. **Understanding must come before scoring, but the verdict follows the full audit.** The conductor delegates coordination to `subagents/change-branch.md`, which resolves `standards_path`, loads the target skill, and invokes `review-skill`.

For both the `review` and `update` gates, invoke the `review-skill` conductor. It applies the review principles from `{standards_path}/reference/review-principles.md` (or the fallback copy in `review-skill/references/REVIEW_PRINCIPLES.md`). After a full audit, it produces a verdict-led report. If the core questions cannot be answered, it produces an incomplete report.

When reviewing a skill with multiple methods or branches, pay special attention to **tooling awareness** and **lazy dependency evaluation**: required dependencies should be checked eagerly, and recommended/optional dependencies should be evaluated lazily per path. The full dependency surface must still be declared in `references/DEPENDENCIES.md` and `skills.json`. When reviewing any skill, check whether it names capabilities before tools, discovers available tools across categories, and discloses degraded sources with user consent. Also check whether the skill overlaps with existing building blocks by invoking `detect-skill-overlap` during comprehension; if the skill is mostly a duplicate or contains a generic capability that should be extracted, record that in the verdict.

After the comprehension step is complete, the `review-skill` conductor runs the remaining workflow:

1. Read the skill files.
2. Comprehend the skill using the review principles.
3. Confirm the comprehension brief with the user — scoring does not start on an unconfirmed understanding.
4. Produce an incomplete report if the core questions cannot be answered.
5. Run `audit-skill` and `validate-skill-frontmatter`.
6. Produce a structured, verdict-led audit report that incorporates the review principles.
7. For the `update` gate, produce a remediation plan, confirm each change, apply approved changes, and run a final audit.

`write-a-skill` delegates the `change` branch to `review-skill` through `subagents/change-branch.md` and consumes the resulting comprehension brief, verdict-led audit report, incomplete report, or remediation plan. When reviewing an existing skill, pay special attention to whether the skill is a separate skill only because it was extracted prematurely. Apply the **Contain** core question from the review principles: *"Should this capability be colocated inside an existing skill, or is extraction into a separate skill justified by reuse?"*

[objective-map]: OBJECTIVE_MAP.md
[fundamentals]: FUNDAMENTALS.md
[pattern-hints]: PATTERN_HINTS.md
[decision-rules]: ../decide-skill-shape/references/DECISION_RULES.md
[review-principles-fallback]: ../review-skill/references/REVIEW_PRINCIPLES.md
[change-branch-subagent]: ../subagents/change-branch.md

