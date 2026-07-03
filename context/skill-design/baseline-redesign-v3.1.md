---
skill: baseline
version: "3.1"
timestamp: 2026-07-03T00:00:00Z
status: design
---

# Redesign: `baseline` skill

## 1. Objective

Capture a reproducible, branch-anchored snapshot of a feature, module, route, API, or bug so that later skills and sessions have a trusted reference point for comparison and verification.

## 2. Skill type, invocation, and scope

| Attribute | Value | Justification |
|---|---|---|
| **Type** | `conductor` | The skill runs a deterministic multi-step workflow and delegates distinct tasks to subagents (scope, method, capture). The main prompt orchestrates workers, handles user input, and writes the final report. |
| **Invocation** | `user-invoked` | Triggered by explicit user phrases (see section 5). |
| **Disable model invocation** | `true` | `baseline` should not be auto-invoked by the model; it is an intentional, evidence-producing step. |
| **Scope** | `global` | The conventions (`.agents/context/`, `.agents/config/`, git state) are project-agnostic and apply across the whole agent workspace. |

## 3. Leading word

**Capture**

The description and every step must anchor on "capture": capture the scope, capture the branch/commit, capture the method, capture the evidence, capture the report. This is the single action the skill performs.

## 4. Boundaries

### In scope

- Resolving scope, branch, commit, and capture method.
- Detecting available capture methods and asking the user when ambiguous.
- Consuming optional context reports from `.agents/context/` (e.g., `debrief`, `handoff`, `plan-next`).
- Capturing evidence via UI/browser, API/HTTP, test runner, code snapshot, or manual fallback.
- Producing the canonical Markdown baseline report and an optional HTML gallery.
- Recording branch, commit, scope, method, and consumed context in report frontmatter.
- Updating `.agents/config/baseline.yaml` with persistent preferences, workarounds, and gotchas.
- Writing and reading a small state file to support resumption.

### Out of scope

- Diagnosing root cause or proposing fixes.
- Implementing changes.
- Comparing before/after states (other skills consume the report).
- Running the project test suite purely for verification; only existing test output is captured as evidence.
- Deploying, releasing, or modifying production systems.

## 5. Triggers

Invoke when the user says any of the following, or the intent is clearly equivalent:

- `baseline`, `baseline this`, `capture a baseline`
- `reproduce`, `reproduce this bug`
- `check the app`, `verify UI`, `verify state`
- `capture state`, `capture the current state`
- `snapshot this feature/module/route`

Also invoke automatically before any change that requires a before/after comparison, or when a bug needs reproducible evidence.

## 6. High-level workflow

1. **Load config and detect capabilities**
   - Done when: `.agents/config/baseline.yaml` has been read, available capture methods have been enumerated, and the default/fallback method is known.

2. **Resolve scope**
   - Done when: a single, unambiguous scope string is recorded and confirmed with the user if the input was vague.

3. **Resolve branch and commit**
   - Done when: the target branch is confirmed, the current commit hash is recorded, and any mismatch with the current branch is either resolved or explicitly acknowledged by the user.

4. **Optionally consume related context**
   - Done when: `.agents/context/` has been scanned for matching reports, the `consumed_context` list is recorded (may be empty), and missing reports are handled gracefully.

5. **Select capture method**
   - Done when: a method is chosen—either from config, by detection, or by user confirmation—and recorded.

6. **Resolve target and authentication**
   - Done when: the URL, endpoint, files, or code range is reachable, and required authentication is configured without hardcoded secrets.

7. **Capture evidence**
   - Done when: artifacts are saved under `.agents/context/baseline/{scope}-{branch}/` and a capture summary exists.

8. **Generate reports**
   - Done when: the Markdown report is written at `.agents/context/baseline/{scope}-{branch}.md` with correct frontmatter, and the optional HTML gallery is generated if requested.

9. **Curate notes and finalize state**
   - Done when: `.agents/config/baseline.yaml` is updated with any new workarounds/preferences/gotchas and the workflow state file is closed/archived.

## 7. State and resumption

### State file

- Location: `.agents/context/baseline/.state/{scope-slug}-{branch-slug}.json`
- Content:
  - `started_at`
  - `scope`
  - `branch`
  - `target_commit`
  - `current_step`
  - `completed_steps`
  - `selected_method`
  - `consumed_context`
  - `artifact_dir`
  - `pending_user_input` (if any)
  - `last_error` (if any)

### Resumption rules

- At the start of the workflow, check for a matching state file.
- If it exists and the recorded `branch`/`commit` still matches the current repo state, resume from `current_step`.
- If it is stale (branch/commit differs), archive it with a `.stale` suffix and start fresh.
- On each step completion, overwrite the state file atomically.
- On successful report generation, archive the state file to `.agents/context/baseline/.state/{scope}-{branch}-completed.json` or delete it.
- If a worker returns `needs_input`, record the pending question in the state file and resume after the user responds.

## 8. Required changes

### `G:/My Drive/.agents/skills/baseline/SKILL.md`

- **Frontmatter**: add `scope: global`, `invocation: user-invoked`, `disable-model-invocation: true`, and bump `version` to `"3.1"`.
- **Skill type**: replace "Workflow skill" with "Conductor" and add a one-line justification.
- **Leading word**: rewrite the description and first paragraph to start with "Capture".
- **Structure**: move `Quick start`, `Report location`, and `Output formats` to `README.md` or references; keep `SKILL.md` focused on intent, triggers, hard stops, process overview, and out-of-scope.
- **Process overview**: add a "Done when" completion criterion for every step.
- **Resumption**: add a short section describing the state file and resume behavior.

### `G:/My Drive/.agents/skills/baseline/README.md`

- Add a table summarizing skill type, invocation, scope, and leading word.
- Add a `State and resumption` section.
- Add an `Evaluation plan` subsection with:
  - Trigger evals: test phrases that must invoke the skill.
  - Behavior evals: missing config, ambiguous scope, no capture method, stale report, user rejects branch, manual fallback.
  - Review cadence: validate on every minor/major version bump and at least quarterly.
- Move `Updating this skill` guidance into a dedicated maintenance section.

### `G:/My Drive/.agents/skills/baseline/references/EXAMPLES.md`

- Update all report frontmatter examples to `version: 3`.
- Replace `ticket:` with `scope:`.
- Add `branch:` and `commit:` fields where missing.
- Update artifact directory names to `{scope}-{branch}` format.
- Update body text to reference the renamed artifact directories.

### `G:/My Drive/.agents/skills/baseline/references/WORKFLOW.md`

- Add a step at the top: "Check for existing state and resume if fresh."
- Add a note at the end of every major step: "Write the state file."
- Reference the state file location and schema.

### `G:/My Drive/.agents/skills/baseline/references/VALIDATION.md`

- Add checks for frontmatter fields: `scope`, `invocation`, `disable-model-invocation`, `leading word`.
- Add checks for state/resumption handling.
- Add checks for the evaluation plan and maintenance cadence.
- Add a check that `EXAMPLES.md` uses the current schema (`version: 3`, `scope:`).

## 9. Files that do NOT need changes

- `G:/My Drive/.agents/skills/baseline/references/DEPENDENCIES.md` — already declares no required skills and correct optional context.
- `G:/My Drive/.agents/skills/baseline/references/CAPABILITIES.md` — method detection and selection rules are consistent.
- `G:/My Drive/.agents/skills/baseline/references/AUTH.md` — no secrets, generic guidance.
- `G:/My Drive/.agents/skills/baseline/references/CONFIG_PATTERN.md` — config schema is sound.
- `G:/My Drive/.agents/skills/baseline/references/PLAYWRIGHT-SETUP.md` — setup guide is independent of these changes.
- `G:/My Drive/.agents/skills/baseline/references/CONTEXT_REPORTS.md` — already uses `version: 3` and `scope:`; only a minor note about state files may be added if desired.

## 10. Self-audit checklist

| Fundamental | Status | Notes |
|---|---|---|
| One core objective | Pass | "Capture a reproducible, branch-anchored snapshot..." |
| Explicit out-of-scope | Pass | Diagnosis, fixes, comparison, deployment excluded. |
| Skill type declared | Pass | Conductor. |
| Invocation declared | Pass | `user-invoked`, `disable-model-invocation: true`. |
| Scope declared | Pass | `global`. |
| Leading word front-loaded | Pass | "Capture". |
| Dependencies declared | Pass | Required capabilities and optional context listed. |
| No secrets | Pass | No hardcoded credentials or env-var names. |
| Harness-agnostic | Pass | Generic tool names and detection patterns. |
| Completion criteria | Pass | Each step has a "Done when" criterion. |
| State/resumption | Pass | State file, freshness rules, and resume logic defined. |
| Eval plan | Pass | Trigger and behavior evals, plus review cadence. |
| Version consistency | Pass | `SKILL.md` 3.1, report `version: 3`, examples updated to 3. |
| Maintenance plan | Pass | Review on version bump and quarterly. |
