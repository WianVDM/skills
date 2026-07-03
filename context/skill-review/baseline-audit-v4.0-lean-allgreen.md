---
status: complete
artifacts:
  - context/skill-review/baseline-audit-v4.0-lean-allgreen.md
---

# Baseline skill audit report

**Skill:** `baseline`  
**Version audited:** `4.0`  
**Auditor:** `write-a-skill` guideline auditor worker  
**Date:** 2026-07-03  
**Scope:** Verify and audit the lean/polished `baseline` skill against the `write-a-skill` rubric.

## Verification findings

| Check | Expected | Result | Evidence |
|---|---|---|---|
| 1. `SKILL.md` version | `version: "4.0"` | ✅ Pass | `skills/baseline/SKILL.md` metadata contains `version: "4.0"`. |
| 2. `CONTEXT_REPORTS.md` report version | `version: 4` | ✅ Pass | `skills/baseline/references/CONTEXT_REPORTS.md` report schema frontmatter and migration notes reference `version: 4`. |
| 3. `EXAMPLES.md` report version | `version: 4` | ✅ Pass | All frontmatter examples in `skills/baseline/references/EXAMPLES.md` contain `version: 4`. |
| 4. `REFERENCE.md` report version | `version: 4` | ✅ Pass | Markdown report template and versioning section in `skills/baseline/references/REFERENCE.md` use `version: 4`. |
| 5. `PLAYWRIGHT-SETUP.md` does not exist | File absent | ✅ Pass | `test -f` returned `NOT_FOUND`. |
| 6. `.gitignore` exists and excludes `__pycache__` | File present, contains `__pycache__/` | ✅ Pass | `skills/baseline/.gitignore` exists and includes `__pycache__/` and `*.py[cod]`. |
| 7. No `debrief`, `handoff`, `plan-next` references | No matches | ✅ Pass | `grep -i` across `skills/baseline/` returned `No matches found`. |
| 8. No `localhost`, `npm run`, `4200`, `1280x720` references | No matches | ✅ Pass | `grep -i` across `skills/baseline/` returned `No matches found`. |
| 9. No `\.cursor`, `\.vscode`, `\.claude`, `\.pi`, `\.kimi` references | No matches | ✅ Pass | `grep` across `skills/baseline/` returned `No matches found`. |

## Summary

Excellent in all aspects. The `baseline` skill at v4.0 is fully aligned with the `write-a-skill` rubric. All verification checks pass, all rubric criteria are green, and there are no blockers. The skill is lean, global, pluggable, and correctly delegates to well-scoped workers with clear return contracts. No harness/vendor-specific or project-specific assumptions leak into core skill files or reference templates.

## Findings table

| Criterion | Rating | Notes |
|---|---|---|
| A1 | Green | Name is lowercase `baseline`, hyphen-separated (none needed), and matches the directory. |
| A2 | Green | Description is well under 1024 characters, states what the skill does, and lists trigger keywords. |
| A3 | Green | Description front-loads the leading word `Capture`; triggers are distinct and cover the branching intent. |
| A4 | Green | Invocation is explicitly `user-invoked` with `disable-model-invocation: true`; matches behavior. |
| B1 | Green | One core objective: capture a reproducible baseline snapshot. |
| B2 | Green | Clear purpose and outcome in `SKILL.md` and `README.md`. |
| B3 | Green | Realistic triggers listed (test app state, reproduce bug, capture pre-change evidence, etc.). |
| B4 | Green | Explicit out-of-scope section lists what the skill does not handle. |
| B5 | Green | Skill type is declared as `conductor` and matches the delegation pattern. |
| C1 | Green | Form is guideline-heavy/conductor with delegated worker prompts; appropriate for the domain. |
| C2 | Green | Every process step in `SKILL.md` ends with a `Done when:` checkable condition. |
| C3 | Green | Completion criteria are checkable and specific (e.g., "artifacts are saved and findings are sufficient"). |
| C4 | Green | Leading word `Capture` anchors behavior throughout the skill. |
| C5 | Green | Rules explain reasoning (e.g., why baseline outputs are excluded, why auth uses env vars). |
| C6 | Green | Every "do not" is paired with a positive directive (e.g., workers "do not ask the user" / "return needs_input"). |
| C7 | Green | No vague guideline soup; each section includes specific criteria or concrete examples. |
| C8 | Green | Skill states intent and outcomes, not low-level mechanics; mechanics live in scripts and workers. |
| C9 | Green | Steps and guidelines are cleanly separated in `SKILL.md` and detailed in `references/`. |
| C10 | Green | No no-op lines; every line in `SKILL.md` and references drives behavior or documentation. |
| D1 | Green | Progressive disclosure followed: overview in `SKILL.md`, detail in `references/`, workers in `subagents/`. |
| D2 | Green | Related concepts grouped under single headings (e.g., process overview, references, hard stops). |
| D3 | Green | `SKILL.md` is lean (3.6 KB); deep detail pushed to `references/` and `subagents/`. |
| D4 | Green | No sediment; `PLAYWRIGHT-SETUP.md` removed and v3 migration path is current. |
| D5 | Green | Each meaning has one authoritative place (report schema in `CONTEXT_REPORTS.md`, templates in `REFERENCE.md`). |
| D6 | Green | `SKILL.md` exists; `README.md` exists for this non-trivial skill. |
| D7 | Green | No empty directories; `references/`, `scripts/`, and `subagents/` all contain content. |
| D8 | Green | All reference links in `SKILL.md` and references resolve to existing files. |
| D9 | Green | Flat structure: one level of `references/`, `scripts/`, and `subagents/`. |
| E1 | Green | Pluggability declared: `scope: global` in `SKILL.md` and "standalone, global conductor" in `README.md`. |
| E2 | Green | Core skill files and references are harness-agnostic; tool-specific logic is isolated in detection scripts. |
| E3 | Green | No hardcoded project tools, paths, or APIs; project values are detected or placeholders. |
| E4 | Green | Detection before config is explicit in the workflow and `CAPABILITIES.md`. |
| E5 | Green | Required skills, capabilities, tools, and env vars are listed in `DEPENDENCIES.md`. |
| E6 | Green | Hard stops are listed and the skill fails closed when capabilities are missing. |
| F1 | Green | Config schema and defaults are documented in `CONFIG_PATTERN.md`. |
| F2 | Green | No secrets stored; credentials referenced via env vars or session files. |
| F3 | Green | Config persists only choices that change future behavior (method, viewport, auth strategy, etc.). |
| F4 | Green | Notes are explicitly future-facing memory (decisions, gotchas, workarounds, preferences). |
| F5 | Green | Workflow states existing config values are never silently overwritten. |
| G1 | Green | State location documented: `.agents/context/baseline/.state/{scope}-{branch}.json`. |
| G2 | Green | State schema and resumption behavior documented in `SKILL.md` and `WORKFLOW.md`. |
| G3 | Green | Resumption logic is explicit: resume if branch/commit match, archive if stale. |
| G4 | Green | Re-runs reuse completed state rather than overwriting. |
| G5 | Green | Report schema requires `skill`, `version`, `scope`, `branch`, `commit`, `method`, `baselined_at`, `type`, `summary`. |
| G6 | Green | Freshness is handled by comparing branch/commit and re-capturing or noting staleness. |
| G7 | Green | Missing consumed reports are handled gracefully; no silent failures. |
| H1 | Green | Workers used for large/isolated tasks: scope resolution, context scanning, method selection, capture. |
| H2 | Green | Each worker prompt states role, scope, tools, forbidden actions, and return format. |
| H3 | Green | Standard worker return contract is defined and referenced in every worker prompt. |
| H4 | Green | Workers return `needs_input` to the conductor; they do not ask the user directly. |
| H5 | Green | Deterministic logic lives in `scripts/` (project type, method detection, git scope, context scan, reachability). |
| H6 | Green | Scripts are read-only, deterministic, bounded, and do not take user input or perform destructive actions. |
| I1 | Green | Required and optional dependencies/consumed reports declared in `DEPENDENCIES.md`. |
| I2 | Green | Shared conventions (report schema, return contract, config pattern) are extracted into reference files. |
| I3 | Green | Missing context reports are handled gracefully; consumers treat them as hints. |
| I4 | Green | One canonical pattern per recurring concern (e.g., one report schema, one state path convention). |
| I5 | Green | Building blocks extracted only where reused or clearly reusable. |
| J1 | Green | No secrets in skill files or reference templates. |
| J2 | Green | Destructive actions (branch switch, config overwrite) require user confirmation. |
| J3 | Green | External access (browser automation, HTTP, MCP) is documented in `CAPABILITIES.md` and `AUTH.md`. |
| J4 | Green | Read-only investigation preferred; capture workers observe and record rather than mutate. |
| J5 | Green | Safe in untrusted projects by default: scripts are read-only, no destructive defaults. |
| K1 | Green | Trigger evals are documented in `README.md` and `VALIDATION.md`. |
| K2 | Green | Behavior and report evals are planned and documented. |
| K3 | Green | Version is `4.0` and report `version` is kept in sync. |
| K4 | Green | Migration path from version 3 is documented in `CONTEXT_REPORTS.md` and `REFERENCE.md`. |
| K5 | Green | Review cadence is documented: validate on every minor/major version bump and at least quarterly. |

## Positive findings

- The skill is fully lean/polished: `SKILL.md` is concise and all deep detail lives in `references/` or `subagents/`.
- The leading word `Capture` is consistently applied across the skill description, README, and worker prompts.
- Worker prompts are exemplary: each clearly states role, scope, in/out-of-scope items, tools, inputs, outputs, and escalation rules.
- The skill is genuinely global/pluggable: no harness vendor names, no project-specific URLs/ports, and no hardcoded paths in core files or reference templates.
- Detection scripts are bounded and read-only; they inspect the environment without mutating it.
- Report schema and migration path from version 3 are clearly documented and version-aligned.
- Security is strong: secrets are referenced via env vars or session files, never stored in skill or config files.
- The `VALIDATION.md` reference provides an internal checklist that already maps closely to the rubric, showing self-consistency.

## Issues

None.

## Decisions made

- Tool-specific detection logic (e.g., Playwright, Cypress, Puppeteer) is allowed inside `scripts/` because it is isolated from the skill contract and reference templates; this aligns with `E2`/`E3` and is explicitly validated in `VALIDATION.md`.
- `README.md` duplication of the `SKILL.md` description is acceptable because the README serves as a human-readable entry point, while `SKILL.md` is the authoritative agent instruction file.

## Open questions

None.

## Blockers

None.
