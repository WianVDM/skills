---
status: blocked
artifacts:
  - context/skill-review/baseline-audit-v4.0-lean-final.md
---

## Summary

The `baseline` skill is **not excellent in all aspects** and **is not ready for release** as the leaned v4.0. The core files and references still carry sediment from earlier versions and from other skills: the declared version is 3.0, report examples still use version 1, specific skill names (`debrief`, `handoff`, `plan-next`) are hardcoded throughout the skill, project-specific defaults (`localhost:4200`, `npm run start`, `1280x720`) remain in reference and config files, and the Playwright setup guide is written as a harness/vendor-specific manual. These are direct violations of the v4.0 lean requirements and are blockers. The skill structure, worker prompts, and detection scripts are otherwise sound and mostly complete, but the surface must be cleaned and version-bumped before the skill can be considered excellent.

## Findings table

| Criterion | Rating | Notes |
|---|---|---|
| A1 | Green | `baseline` is lowercase, hyphen-separated, and matches the directory name. |
| A2 | Green | Description is under 1024 characters and lists clear trigger keywords. |
| A3 | Green | Leading word "Capture" anchors the description; triggers are one per branch with no duplicates. |
| A4 | Red | `SKILL.md` does not explicitly declare an invocation mode (`model-invoked` or `user-invoked`). The description implies user invocation, but the required declaration is missing. |
| B1 | Green | One core objective: capture a reproducible snapshot of current state. |
| B2 | Green | `SKILL.md` clearly states the purpose and outcome. |
| B3 | Green | Realistic triggers are listed under "When to use" and the description. |
| B4 | Green | Explicit "Out of scope" section lists what the skill does not handle. |
| B5 | Green | Skill type is declared as a standalone workflow skill. |
| C1 | Green | Form is instruction-heavy and appropriate for a workflow skill. |
| C2 | Yellow | Process overview steps are high-level and do not each end with a concrete, checkable completion condition. Hard stops are clearer than the main workflow steps. |
| C3 | Yellow | Completion criteria are strong for hard stops but weak for the main process steps. |
| C4 | Green | Leading word "Capture" is used consistently. |
| C5 | Green | Rules generally explain reasoning (e.g., why to ask before switching branches). |
| C6 | Green | "Do not" directives are paired with positive alternatives (e.g., ask before switching branches). |
| C7 | Green | Guidelines are specific and avoid vague soup. |
| C8 | Green | Intent is stated, not mechanics. |
| C9 | Green | Steps and guidelines are clearly separated. |
| C10 | Green | No obvious no-op lines; every line changes behavior. |
| D1 | Green | Progressive disclosure is followed: overview in `SKILL.md`, detail in `references/`. |
| D2 | Green | Related concepts are grouped under single headings. |
| D3 | Green | `SKILL.md` is lean and pushes detail to references. |
| D4 | Red | Stale guidance remains: references to `debrief`/`handoff`/`plan-next`, version 3.0 in `SKILL.md`, version 3 in `CONTEXT_REPORTS.md`/`REFERENCE.md`, version 1 in `EXAMPLES.md`. |
| D5 | Yellow | Some duplication exists: hard-stop lists are repeated across `SKILL.md`, `WORKFLOW.md`, and `REFERENCE.md`. |
| D6 | Green | `SKILL.md` and `README.md` are present. |
| D7 | Green | All directories (`references/`, `subagents/`, `scripts/`) contain content. |
| D8 | Green | All reference links in `SKILL.md` resolve to existing files. |
| D9 | Green | Structure is flat (skill root → references/subagents/scripts). |
| E1 | Red | Pluggability is not explicitly declared as global or project-specific. The skill is project-oriented (uses `.agents/config/`) but never states its portability class. |
| E2 | Red | `references/PLAYWRIGHT-SETUP.md` contains harness/vendor-specific paths (`~/.kimi/mcp.json`, `~/.claude/mcp.json`, `~/.cursor/mcp.json`, `.vscode/mcp.json`). These are in a reference file, not a detection script. |
| E3 | Red | Project-specific defaults persist: `http://localhost:4200`, `npm run start`, and `1280x720` appear in `CONFIG_PATTERN.md`, `REFERENCE.md`, `PLAYWRIGHT-SETUP.md`, and `EXAMPLES.md`. The `viewport: 1280x720` default in `CONFIG_PATTERN.md` is a hardcoded project-specific value. |
| E4 | Green | Detection precedes configuration; capabilities are detected before asking the user. |
| E5 | Green | `DEPENDENCIES.md` declares required skills, optional context, required capabilities, and environment variables. |
| E6 | Green | Hard stops and fallback behavior make missing capabilities fail closed. |
| F1 | Green | `CONFIG_PATTERN.md` documents the config schema and defaults. |
| F2 | Green | Secrets are referenced via env vars or session files; no plaintext credentials. |
| F3 | Green | Config is limited to choices that change future behavior. |
| F4 | Green | Notes are documented as memory that changes future behavior. |
| F5 | Green | User consultation rules forbid silent overwrites. |
| G1 | Green | State locations are documented: reports in `.agents/context/baseline/`, config in `.agents/config/baseline.yaml`. |
| G2 | Green | Frontmatter and body structure are documented in `CONTEXT_REPORTS.md` and `REFERENCE.md`. |
| G3 | Yellow | Resumption after context compaction is not explicitly addressed. The skill has workers but no clear "resume from state" path. |
| G4 | Green | `REFERENCE.md` states to reuse existing artifacts when fresh and overwrite only when re-capturing. |
| G5 | Green | Report schema is documented with required fields and definitions. |
| G6 | Green | Freshness conditions are documented (branch/commit/scope/method mismatch). |
| G7 | Green | Missing optional context reports are handled gracefully; explicit missing required reports trigger consultation. |
| H1 | Green | Workers are used for large, isolated tasks (capture, context scanning, method selection, scope resolution). |
| H2 | Green | Each worker prompt defines role, scope, tools, forbidden actions, and return format. |
| H3 | Green | Workers reference the standard worker return contract. |
| H4 | Green | Workers return `needs_input` rather than asking the user directly. |
| H5 | Green | Deterministic logic lives in `scripts/*.py` (project detection, method detection, git resolution, etc.). |
| H6 | Green | Scripts are read-only, deterministic, and do not take destructive actions or user input. |
| I1 | Green | Dependencies and consumed reports are declared in `DEPENDENCIES.md` and `CONTEXT_REPORTS.md`. |
| I2 | Yellow | The optional-consumed-context pattern is not extracted into a generic building block; specific skill names are hardcoded. |
| I3 | Green | Missing optional context is handled gracefully and does not cause silent failures. |
| I4 | Green | One canonical worker return contract is used across all subagents. |
| I5 | Green | No premature abstraction; building blocks are only extracted where reused. |
| J1 | Green | No secrets are stored in skill files. |
| J2 | Green | Destructive actions (branch switches, overwrites) require explicit user confirmation. |
| J3 | Green | External access (Playwright MCP, API calls) is documented. |
| J4 | Green | Read-only investigation is preferred; scripts only inspect files. |
| J5 | Green | Safe in untrusted projects by default; no destructive or mutating actions. |
| K1 | Red | No trigger evals are documented or planned. |
| K2 | Red | No behavior tests or with-skill/baseline runs are documented or planned. `VALIDATION.md` is a manual checklist, not executed tests. |
| K3 | Red | Version is not v4.0. `SKILL.md` shows `version: "3.0"`; `CONTEXT_REPORTS.md` and `REFERENCE.md` show `version: 3`; `EXAMPLES.md` shows `version: 1`. `README.md` has no version field. |
| K4 | Green | Migration path for older reports is documented in `REFERENCE.md`. |
| K5 | Red | No maintenance plan or scheduled review after real-world usage is documented. |

## Positive findings

- The skill has a clear, single objective and a well-defined workflow.
- Progressive disclosure is good: `SKILL.md` is concise and references provide depth.
- Worker prompts are well bounded, use the standard return contract, and do not ask users directly.
- Detection scripts are read-only, deterministic, and safe.
- Config schema is documented and avoids storing secrets.
- Hard stops and fallback behavior are clearly stated.
- Report schema and freshness rules are documented.

## Issues

- [red] **A4 — Invocation mode not declared.** `SKILL.md` does not explicitly state whether the skill is `model-invoked` or `user-invoked`.
- [red] **D4 — Stale guidance and sediment remain.** References to `debrief`, `handoff`, and `plan-next` are hardcoded in core files and references. Report versions (3, 1) and skill version (3.0) do not match the target v4.0.
- [red] **E1 — Pluggability not declared.** The skill never explicitly states whether it is global or project-specific.
- [red] **E2 — Harness/vendor-specific paths in references.** `references/PLAYWRIGHT-SETUP.md` contains `~/.kimi/mcp.json`, `~/.claude/mcp.json`, `~/.cursor/mcp.json`, and `.vscode/mcp.json`.
- [red] **E3 — Project-specific defaults remain.** `http://localhost:4200`, `npm run start`, and `1280x720` appear in `CONFIG_PATTERN.md`, `REFERENCE.md`, `PLAYWRIGHT-SETUP.md`, and `EXAMPLES.md`. The default `viewport: 1280x720` in config is a hardcoded value.
- [red] **K1 — No trigger evals planned.** There is no evidence of description testing or trigger evaluations.
- [red] **K2 — No behavior tests planned.** `VALIDATION.md` is a manual checklist; no automated or planned with-skill/baseline runs are documented.
- [red] **K3 — Version not v4.0.** `SKILL.md` = 3.0, `CONTEXT_REPORTS.md` = 3, `REFERENCE.md` = 3, `EXAMPLES.md` = 1; `README.md` has no version.
- [red] **K5 — No maintenance plan.** No scheduled review or real-world usage feedback loop is documented.
- [yellow] **C2/C3 — Process steps lack explicit completion criteria.** Steps are high-level; each should end with a checkable condition.
- [yellow] **D5 — Minor duplication.** Hard-stop lists are repeated across `SKILL.md`, `WORKFLOW.md`, and `REFERENCE.md`.
- [yellow] **G3 — Resumption logic not explicit.** The skill does not document how it resumes after context compaction.
- [yellow] **I2 — Specific skill references not abstracted.** Optional consumed context could be described generically rather than naming `debrief`, `handoff`, `plan-next`.
- [yellow] **No `.gitignore` in skill directory.** `__pycache__/*.pyc` files are present in `scripts/`. Although the audit instructions treat these as excluded by `.gitignore`, the skill itself has no `.gitignore` file, which is a hygiene gap.

## Decisions made

- Treated the presence of `__pycache__/*.pyc` as excluded per the audit instructions, but flagged the missing `.gitignore` as a hygiene issue because the user explicitly asked to verify `.gitignore` excludes it.
- Applied the strict interpretation of "no references to specific other skills" and "no project-specific defaults" to both core files and references, as required.
- Treated `PLAYWRIGHT-SETUP.md` as a reference file, so its harness/vendor-specific paths are a red finding despite the detection scripts being allowed tool-specific logic.
- Did not execute or compile Python scripts, as instructed; script assessment is based on static review.
- Did not modify baseline files; all findings are reported only.

## Open questions

- Should the optional consumed-context section be removed entirely, or replaced with a generic "scan for related context reports" instruction with no named skills?
- Should `PLAYWRIGHT-SETUP.md` be removed, moved to a harness-specific location, or rewritten to only describe how to detect an MCP server generically?
- Should `EXAMPLES.md` be rewritten to remove all project-specific values, or can it keep illustrative values if clearly marked as examples only?
- What is the intended test harness for trigger evals and behavior tests (K1/K2)?

## Blockers

- Version must be bumped to 4.0 in `SKILL.md` and `README.md`, and report version must be 4 in `CONTEXT_REPORTS.md`, `REFERENCE.md`, and `EXAMPLES.md`.
- All references to `debrief`, `handoff`, and `plan-next` must be removed from core files and references (or replaced with generic "related context reports" language).
- All project-specific defaults (`localhost:4200`, `npm run start`, `1280x720`) must be removed from core files and references, including the default `viewport` in `CONFIG_PATTERN.md`.
- Harness/vendor-specific paths and tool names must be removed from `references/PLAYWRIGHT-SETUP.md`.
- Invocation mode must be explicitly declared in `SKILL.md`.
- Pluggability (global vs project-specific) must be explicitly declared.
- Trigger evals and behavior tests must be documented or planned (K1/K2).
- A maintenance plan must be documented (K5).
- A `.gitignore` excluding `__pycache__/` and `*.pyc` should be added to the skill directory.
