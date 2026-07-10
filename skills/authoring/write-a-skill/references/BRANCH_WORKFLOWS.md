# Branch workflows

This reference holds the detailed step-by-step workflows for each `write-a-skill` internal gate. `SKILL.md` keeps the top-level branch summary and completion criterion; reach this file when the conductor needs the full phase list for a gate.

Top-level branches:

- **Create branch** — for producing a new skill or deciding what shape to build. Internal gates: `full`, `quick`, `decide`.
- **Change branch** — for auditing or updating an existing skill. Internal gates: `review`, `update`.

## Conventions

- Each phase ends with a **completion criterion**.
- The conductor does not advance to the next phase until the criterion is met or the user explicitly overrides it.
- Destructive actions (writing, overwriting, installing) always require explicit approval.

## Create branch

### Create branch — full gate

This is the full design workflow for a new skill from scratch.

#### 1. Clarify intent

**Why:** designing the wrong skill is expensive. Clarifying intent first prevents building a solution for the wrong problem.

Understand the problem, trigger, success criteria, and whether a skill is warranted. Use grill-me-style questions with proposed defaults.

**Completion criterion:** the intent note contains the problem, trigger, success criteria, and the chosen gate `full`.

#### 2. Explore alternatives

**Why:** a new skill should be the last resort, not the first.

Run `list-available-skills` and `search-skills-registry` to find existing skills, scripts, MCP servers, or context files that might cover the problem.

**Completion criterion:** the alternatives report lists existing options and gives a clear recommendation: build new skill, reuse/extend existing skill, or use an alternative.

#### 3. Decide shape and colocation

**Why:** the shape of the solution determines every later decision, and whether the capability should live inside an existing skill determines whether a new skill is warranted at all.

Confirm with the user that a new skill is the right shape, not a script, MCP server, context file, or installed skill. Then apply the colocation principle: if the capability is only used by one existing skill, recommend colocating it inside that skill unless extraction is justified by reuse (cross-cutting concern, multiple current consumers, stable narrow interface, or generic-domain problem).

**Completion criterion:** the user confirms the chosen shape is a new skill and that extraction is justified, or agrees to colocate the capability inside an existing skill.

#### 4. Define identity

**Why:** a confirmed identity is the contract that prevents scope creep and naming drift.

Produce a frontmatter skeleton: name, description, invocation. Add `version` only if the user requires it or the skill will be shared or consumed. Add harness hints such as `depends` only if the target harness requires them.

**Completion criterion:** the design draft contains an identity section and the user has confirmed it.

#### 5. Define scope

**Why:** clear boundaries prevent bloat and hidden assumptions.

Write one core objective, explicit in-scope items, and explicit out-of-scope items.

**Completion criterion:** the scope boundaries are explicit and do not contradict each other.

#### 6. Select patterns and capability-to-tool strategy

**Why:** applying the right patterns makes the skill portable, maintainable, and composable. Designing the capability-to-tool strategy up front prevents adapter tunnel vision.

Apply the fundamentals from [references/FUNDAMENTALS.md][fundamentals] and select Layer 2 patterns using [PATTERN_HINTS.md][pattern-hints]. For each load-bearing capability, build a capability matrix (preferred tool, fallback tools, degraded-output disclosure, user-consent behavior) using the guidance in [PATTERN_HINTS.md][pattern-hints]. For dependencies, decide:

- Which are **required** and must be checked at initialization.
- Which are **recommended** or **optional** and can be evaluated **lazily** when the relevant method or branch is selected.

Document the lazy evaluation strategy and the capability-to-tool matrix in the design draft so the drafted skill does not ask the user to configure unrelated tooling upfront.

**Completion criterion:** the pattern list exists, the capability-to-tool matrix covers every load-bearing capability, the dependency evaluation strategy is documented, and the user has confirmed it.

#### 7. Draft artifacts

**Why:** only after the design is approved does the skill produce concrete files. Drafting is the execution of the design, not the design itself.

Generate `SKILL.md`, optional `README.md`, references, subagents, scripts, and assets/templates.

**Completion criterion:** all files in the approved design are created and the directory structure matches the design.

#### 8. Audit and validate

**Why:** the design may pass, but the drafted files can still drift.

Run `audit-skill` and `validate-skill-frontmatter`. Fix blockers before showing the result to the user.

**Completion criterion:** the audit report exists with no blocking failures, or the user has explicitly recorded a reason for overriding a blocker.

#### 9. Generate evals

**Why:** model-invoked skills need trigger evals to be testable and reliable.

Run `run-trigger-evals` for model-invoked skills. If the user declines, record the decision in the decision log.

**Completion criterion:** `evals/evals.json` exists or the user has explicitly declined.

#### 10. Confirm and write

**Why:** drafting files without approval is the most common destructive action in this skill.

Present the design, audit, and alternatives summary. Write files only after explicit approval.

**Completion criterion:** the user has explicitly approved the design and files are written.

### Create branch — quick gate

A compressed version of the full gate for minimal skills.

1. **Clarify intent** (minimal) — capture problem, trigger, and success criteria.
2. **Explore alternatives** (light) — check existing skills and simple alternatives.
3. **Decide shape and colocation** — name, description, invocation; decide whether to colocate inside an existing skill or extract as a new reusable skill.
4. **Define scope** — one objective, in-scope, out-of-scope.
5. **Select patterns** — apply fundamentals.
6. **Design capability-to-tool strategy** — for each load-bearing capability, note the preferred tool, fallback, and degraded-output disclosure.
7. **Draft** — write the skill files.
8. **Audit** — run `audit-skill` and `validate-skill-frontmatter`.
9. **Confirm and write** — get approval before writing.

### Create branch — decide gate

For the full decide workflow, invoke the `decide-skill-shape` skill. It will:

1. Capture the problem.
2. Explore existing solutions using `list-available-skills` and `search-skills-registry`.
3. Ask classification questions.
4. Apply the decision rules from [decide-skill-shape/references/DECISION_RULES.md][decision-rules].
5. Present a recommendation with alternatives and trade-offs.
6. Write a decision report to `{context}/decide-skill-shape/{key}-decision-report.md`.

`write-a-skill` consumes the decision report and offers the user the next step. The `decide` gate does not write skill files.

## Change branch

The `change` branch audits or updates an existing skill. **Understanding must come before scoring, but the verdict follows the full audit.**

For both the `review` and `update` gates, invoke the `review-skill` conductor. It applies the review principles from [docs/skill-standards/reference/review-principles.md][review-principles] (or the fallback copy in [review-skill/references/REVIEW_PRINCIPLES.md][review-principles-fallback]). After a full audit, it produces a verdict-led report. If the core questions cannot be answered, it produces an incomplete report.

When reviewing a skill with multiple methods or branches, pay special attention to **tooling awareness** and **lazy dependency evaluation**: required dependencies should be checked eagerly, and recommended/optional dependencies should be evaluated lazily per path. The full dependency surface must still be declared in `references/DEPENDENCIES.md` and `skills.json`. When reviewing any skill, check whether it names capabilities before tools, discovers available tools across categories, and discloses degraded sources with user consent.

After the comprehension step is complete, the `review-skill` conductor runs the remaining workflow:

1. Read the skill files.
2. Comprehend the skill using the review principles.
3. Produce an incomplete report if the core questions cannot be answered.
4. Run `audit-skill` and `validate-skill-frontmatter`.
5. Produce a structured, verdict-led audit report that incorporates the review principles.
6. For the `update` gate, produce a remediation plan, confirm each change, apply approved changes, and run a final audit.

`write-a-skill` delegates the `change` branch to `review-skill` and consumes the resulting comprehension brief, verdict-led audit report, incomplete report, or remediation plan. When reviewing an existing skill, pay special attention to whether the skill is a separate skill only because it was extracted prematurely. Apply the **Contain** core question from the review principles: *"Should this capability be colocated inside an existing skill, or is extraction into a separate skill justified by reuse?"*

[fundamentals]: FUNDAMENTALS.md
[pattern-hints]: PATTERN_HINTS.md
[decision-rules]: ../decide-skill-shape/references/DECISION_RULES.md
[review-principles]: ../../../../docs/skill-standards/reference/review-principles.md
[review-principles-fallback]: ../review-skill/references/REVIEW_PRINCIPLES.md

### Change branch — review gate (legacy inline detail)

1. **Read the skill** — load all files.
2. **Comprehend the skill** — apply the review principles from `docs/skill-standards/reference/review-principles.md`.
3. **Produce an incomplete report** if the core questions cannot be answered.
4. **Run `audit-skill`** — evaluate against the rubric, informed by the comprehension step.
5. **Run `validate-skill-frontmatter`** — check schema compliance.
6. **Produce a verdict-led report** — lead with a verdict, then findings and optional update path.

### Change branch — update gate (legacy inline detail)

1. **Read the skill** — load `SKILL.md`, `README.md`, references, subagents, scripts, and assets.
2. **Comprehend the skill** — apply the review principles from `docs/skill-standards/reference/review-principles.md`.
3. **Produce an incomplete report** if the core questions cannot be answered.
4. **Run `audit-skill`** — evaluate against the rubric, informed by the comprehension step.
5. **Run `validate-skill-frontmatter`** — check schema compliance.
6. **Produce remediation plan** — list concrete changes with effort estimates and rationale.
7. **Confirm before applying** — present the plan; apply changes only after explicit approval.
8. **Run final audit** — close the loop.
