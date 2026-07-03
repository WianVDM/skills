---
status: complete
artifacts:
  - context/skill-review/baseline-audit-v4.0-lean-verified.md
---

# `baseline` skill v4.0 audit report

Audited against `skills/write-a-skill/references/AUDIT_RUBRIC.md`.

## Verification findings

1. `skills/baseline/SKILL.md` frontmatter: `version: "4.0"` ✅
2. `skills/baseline/references/CONTEXT_REPORTS.md` report schema: `version: 4` ✅
3. `skills/baseline/references/EXAMPLES.md` first example frontmatter: `version: 4` ✅
4. `skills/baseline/references/REFERENCE.md` Markdown template: `version: 4` ✅
5. `skills/baseline/references/PLAYWRIGHT-SETUP.md` exists? **No** — file is not present. This is the expected/correct state; no separate Playwright setup doc is required. ✅
6. `skills/baseline/.gitignore` exists and contains `__pycache__`? **Yes** — file exists and contains `__pycache__/`. ✅
7. `debrief`, `handoff`, or `plan-next` appear in `skills/baseline/`? **No matches found.** ✅
8. `localhost`, `npm run`, `4200`, or `1280x720` appear in `skills/baseline/`? **No matches found.** ✅
9. `\.cursor`, `\.vscode`, `\.claude`, `\.pi`, or `\.kimi` appear in `skills/baseline/`? **No matches found.** ✅

## Summary

Excellent in all aspects. The `baseline` skill at v4.0 is well-structured, fully global/pluggable, and safe. All verification checks pass. The skill cleanly separates intent in `SKILL.md` from detailed guidance in `references/`, declares no dependencies, handles state and resumption, and documents its report schema, config, auth, and evaluation plan. Only two minor stylistic improvements were identified; neither is a blocker.

## Findings table

| Criterion | Rating | Notes |
|---|---|---|
| A1 | Green | Name `baseline` is lowercase, hyphen-separated, and matches directory. |
| A2 | Green | Description states purpose, outcome, and trigger keywords; under 1024 characters. |
| A3 | Yellow | Description front-loads "Capture", but all trigger keywords are packed into a single `or` clause rather than one trigger per branch. Consider splitting into separate branches for readability. |
| A4 | Green | `invocation: user-invoked` and `disable-model-invocation: true` are explicit and consistent. |
| B1 | Green | One core objective: capture a reproducible snapshot. |
| B2 | Green | `SKILL.md` clearly states what it does and the snapshot outcome. |
| B3 | Green | Realistic triggers listed (`baseline`, `reproduce`, `verify UI`, etc.). |
| B4 | Green | Explicit "Out of scope" section lists what it does not handle. |
| B5 | Green | Declared as `Conductor`; delegates to focused workers. |
| C1 | Green | Form is guideline/instruction hybrid appropriate for a conductor skill. |
| C2 | Green | Process overview steps each end with a "Done when:" criterion. |
| C3 | Green | Completion criteria are concrete and checkable. |
| C4 | Green | Leading word "Capture" anchors behavior. |
| C5 | Green | Rules explain reasoning (e.g., exclude baseline outputs to avoid circular self-reference). |
| C6 | Green | Negations are paired with positive directives (e.g., "Stop and ask for direction"). |
| C7 | Green | Guidelines are specific; no vague soup. |
| C8 | Green | Intent is stated; mechanics live in references and scripts. |
| C9 | Green | Steps and guidelines are cleanly separated. |
| C10 | Green | Every section in `SKILL.md` changes behavior versus the default. |
| D1 | Green | Progressive disclosure: overview in `SKILL.md`, detail in `references/`. |
| D2 | Green | Related concepts grouped under single headings. |
| D3 | Green | `SKILL.md` is lean; deep detail is pushed to references. |
| D4 | Green | No stale guidance detected; v3 migration notes are intentional. |
| D5 | Green | Each meaning has one authoritative place (e.g., report schema only in `CONTEXT_REPORTS.md` and `REFERENCE.md`). |
| D6 | Green | `SKILL.md` exists; `README.md` present for non-trivial skill. |
| D7 | Green | No empty directories; `references/`, `scripts/`, and `subagents/` all contain content. |
| D8 | Green | All reference links in `SKILL.md` and `README.md` resolve to existing files. |
| D9 | Green | Structure is flat (`references/`, `scripts/`, `subagents/`). |
| E1 | Green | `scope: global` in frontmatter; README confirms global. |
| E2 | Green | Core skill files and references avoid harness-specific tool names, slash commands, or vendor APIs. Detection scripts are project-agnostic in contract. |
| E3 | Green | Project-specific values (URLs, ports, commands) are placeholders, null, or detection-based. |
| E4 | Green | Detection of project type, capture methods, and runtime precedes user questions. |
| E5 | Green | `DEPENDENCIES.md` declares required skills, capabilities, tools, and env vars. |
| E6 | Green | Hard stops when required capabilities are missing (scope, branch, target, method, auth). |
| F1 | Green | Config schema documented in `CONFIG_PATTERN.md`. |
| F2 | Green | Auth uses env-var references and session files; no hardcoded secrets. |
| F3 | Green | Config persists only choices that change future behavior. |
| F4 | Green | Notes are future-facing (`workaround`, `preference`, `gotcha`, `decision`, `assumption`). |
| F5 | Green | `CONFIG_PATTERN.md` explicitly forbids silently overwriting existing config. |
| G1 | Green | State location documented: `.agents/context/baseline/.state/{scope}-{branch}.json`. |
| G2 | Green | State fields (`scope`, `branch`, `target_commit`, `current_step`, `selected_method`, `consumed_context`) documented in `WORKFLOW.md`. |
| G3 | Green | Resume from matching state; archive stale state; record pending `needs_input`. |
| G4 | Green | Re-runs reuse completed state instead of overwriting. |
| G5 | Green | Report schema documents `skill`, `version`, `scope`, `branch`, `commit`, `method`, `baselined_at`, `type`, and `summary`. |
| G6 | Green | Freshness handled by branch/commit comparison; stale reports trigger re-capture or warning. |
| G7 | Green | Missing consumed reports handled gracefully; explicit fallback on missing expected reports. |
| H1 | Green | Workers used for isolated tasks: context scout, scope resolver, method selector, capture worker. |
| H2 | Yellow | Each worker prompt states role, scope, forbidden actions, and return format, but does not explicitly enumerate the tools the worker may use. Add a brief "Tools" section or inherit reference to clarify. |
| H3 | Green | Standard worker return contract (`status`, `artifacts`, `summary`, `findings`, `decisions made`, `open questions`, `blockers`) is defined and referenced. |
| H4 | Green | Workers return `needs_input` to the conductor; do not ask users directly. |
| H5 | Green | Deterministic logic lives in `scripts/` (detect, resolve, scan, check). |
| H6 | Green | Scripts are read-only, deterministic, and do not take user input or perform destructive actions. |
| I1 | Green | Dependencies and consumed reports declared in `DEPENDENCIES.md` and `CONTEXT_REPORTS.md`. |
| I2 | Green | Shared conventions (report schema, config pattern, worker contract) are extracted. |
| I3 | Green | Missing dependencies/context reports are noted or consulted, not silently ignored. |
| I4 | Green | One canonical default approach per recurring problem (e.g., report schema, config bootstrap). |
| I5 | Green | Building blocks extracted only where reused or clearly reusable. |
| J1 | Green | No secrets found in skill files or config defaults. |
| J2 | Green | Branch switching and destructive actions require explicit user confirmation. |
| J3 | Green | External access (auth methods, APIs) declared in `AUTH.md`. |
| J4 | Green | Read-only investigation preferred; capture only, no changes. |
| J5 | Green | Safe in untrusted projects by default: read-only scripts, no silent writes, hard stops. |
| K1 | Green | Trigger evals documented in `README.md` and `VALIDATION.md`. |
| K2 | Green | Behavior evals (happy path, missing config, ambiguous scope, manual fallback, etc.) documented. |
| K3 | Green | Version is `4.0`; report `version` is `4` in sync. |
| K4 | Green | Migration path from version 3 documented in `CONTEXT_REPORTS.md` and `REFERENCE.md`. |
| K5 | Green | Maintenance plan documented: review on every minor/major version bump and at least quarterly. |

## Positive findings

- Skill is fully standalone and global; no required peer skills.
- Report schema is clean, versioned, and includes a mandatory one-sentence summary.
- State and resumption are well documented with branch/commit freshness checks.
- Configuration handling respects existing user preferences and avoids silent overwrites.
- Scripts are read-only, deterministic, and project-agnostic in their contract.
- No harness-specific, project-specific, or editor-specific leakage found in skill files.
- Evaluation and maintenance plan are explicit.

## Issues

- [yellow] A3: Description packs all trigger keywords into a single `or` clause. Recommendation: split into separate trigger branches (e.g., "Use when the user wants to test current app state, reproduce a bug, capture pre-change evidence, or mentions one of these keywords: `baseline`, `reproduce`, `check the app`, `verify UI`, `capture state`, `snapshot`.").
- [yellow] H2: Worker prompts do not explicitly list the tools available to the worker. Recommendation: add a "Tools" section to each worker prompt or reference the shared tool contract so the worker knows which tools it may invoke.

## Decisions made

- Treated `PLAYWRIGHT-SETUP.md` absence as a passing verification check because the skill deliberately does not require a dedicated Playwright setup doc; capability detection is vendor-agnostic.
- Treated H2 as yellow rather than red because the subagent harness implicitly provides tools, and the absence of an explicit list does not block execution.

## Open questions

- None.

## Blockers

- None.
