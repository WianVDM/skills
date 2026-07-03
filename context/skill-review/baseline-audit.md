---
skill: baseline
version: "3.0"
timestamp: 2026-07-03T00:00:00Z
auditor: write-a-skill (Review branch)
---

# Baseline skill review

## Core idea

`baseline` captures a reproducible snapshot of a feature, module, implementation, or bug on a specific branch. The snapshot is evidence that other skills and future sessions can rely on when planning, implementing, or verifying changes. It answers: *"What is the current state, at this commit, on this branch?"*

## Why it exists

Before changing anything, you need to know what the current state is. Bugs need reproduction evidence. Features need pre-change UI/API snapshots. Refactors need code-state anchors. Without a baseline, later work has no trusted reference point to compare against or return to.

## What it does

- Resolves scope, branch, commit, and capture method.
- Captures evidence via UI, API, test, code snapshot, or manual fallback.
- Writes a canonical Markdown report (and optional HTML gallery) to `.agents/context/baseline/`.
- Records branch, commit, method, scope, and consumed context in report frontmatter.
- Updates `.agents/config/baseline.yaml` with preferences, workarounds, and gotchas.

## When to use

- The user says `baseline`, `reproduce`, `check the app`, `verify UI`, or `capture state`.
- Before implementing a change that needs a before/after comparison.
- When a bug needs reproducible evidence.
- When a feature or route needs pre-change documentation.

## How it works

1. **Load config** — read `.agents/config/baseline.yaml` and shared config.
2. **Detect capabilities** — discover available capture methods (UI, API, test, code snapshot, manual).
3. **Resolve scope** — from user input, context reports, or by asking.
4. **Resolve branch/commit** — confirm branch and record current commit.
5. **Resolve method** — pick or ask for the capture method.
6. **Resolve target/auth** — confirm URL, endpoint, files, or auth method.
7. **Capture** — execute the chosen method via a worker.
8. **Generate artifacts and reports** — save evidence and write Markdown/HTML reports.
9. **Curate notes** — update config with preferences and gotchas.

## Classification

| Attribute | Current value | Assessment |
|---|---|---|
| Type | Declared as "Workflow skill" | Not a standard type. Best fits **hybrid** (workflow + guidelines) or **conductor** because it delegates to subagents. |
| Invocation | Implicitly user-invoked | Not declared in frontmatter. |
| Scope | Not declared | Should be global. |
| Leading word | Missing | "Capture" is the natural leading word but not front-loaded. |
| Portability | Mostly global | Uses project-agnostic conventions and detection, but mentions specific tools and MCPs. |

## Audit findings

### A. Identity and invocation

| Id | Rating | Notes |
|---|---|---|
| A1 | Green | `baseline` matches directory; lowercase hyphen-separated. |
| A2 | Green | Description is under 1024 chars and lists triggers. |
| A3 | Red | No leading word front-loaded. "Capture" appears but is not used as the anchor. |
| A4 | Red | `invocation` and `disable-model-invocation` are not declared in frontmatter. |

### B. Objective and scope

| Id | Rating | Notes |
|---|---|---|
| B1 | Green | One core objective: capture reproducible snapshots. |
| B2 | Green | Purpose is clear in description and README. |
| B3 | Green | Triggers listed in `When to use`. |
| B4 | Green | `Out of scope` is explicit. |
| B5 | Yellow | Declared as "Workflow skill", which is not a standard type. Should be **hybrid** or **conductor**. |

### C. Form and style

| Id | Rating | Notes |
|---|---|---|
| C1 | Yellow | Hybrid form, but the mix of steps and guidelines is not clearly signaled. |
| C2 | Red | `Process overview` lists steps without completion criteria in `SKILL.md`. Criteria live only in `references/WORKFLOW.md`. |
| C3 | N/A | No completion criteria in SKILL.md to evaluate. |
| C4 | Red | No leading word anchors behavior. |
| C5 | Yellow | Some rules explain reasoning; others are implicit. |
| C6 | Green | Negations are generally paired with directives (e.g., "Do not silently switch branches" → "ask the user"). |
| C7 | Yellow | Some sections are vague at the top level (e.g., "Curate notes"). |
| C8 | Yellow | `SKILL.md` reads partly like a manual (process overview) and partly like a reference. |
| C9 | Green | Steps and guidelines are generally separated by headings. |
| C10 | Green | No obvious no-op lines. |

### D. Information hierarchy and structure

| Id | Rating | Notes |
|---|---|---|
| D1 | Green | Progressive disclosure is good. Detail lives in `references/`. |
| D2 | Green | Related concepts are grouped. |
| D3 | Yellow | `SKILL.md` is 4,021 bytes. Could be leaner; some detail could move to references. |
| D4 | Green | No stale guidance detected. |
| D5 | Green | No duplication in SKILL.md. |
| D6 | Green | Required files and references are present. |
| D7 | Green | No empty directories. |
| D8 | Green | All reference links in SKILL.md resolve. |
| D9 | Green | Flat structure. |

### E. Global vs project-specific

| Id | Rating | Notes |
|---|---|---|
| E1 | Red | `scope` is not declared in frontmatter. |
| E2 | Green | Mentions tools generically (Playwright, Cypress, curl) rather than harness-specific commands. MCP is a standard capability layer. |
| E3 | Green | Uses `.agents/context/` and `.agents/config/` conventions; no hardcoded project paths. |
| E4 | Green | Detects environment before config. |
| E5 | Green | Dependencies are declared in `DEPENDENCIES.md`. |
| E6 | Green | Hard-stop conditions are documented. |

### F. Configuration

| Id | Rating | Notes |
|---|---|---|
| F1 | Green | Config schema is documented in `CONFIG_PATTERN.md`. |
| F2 | Green | No secrets in skill files. |
| F3 | Green | Config is persisted only for choices that change future behavior. |
| F4 | Green | Notes are memory; logs are not notes. |
| F5 | Green | No silent overwrites. |

### G. State and context

| Id | Rating | Notes |
|---|---|---|
| G1 | Green | State/report locations are documented. |
| G2 | Green | Report schema is documented in `CONTEXT_REPORTS.md`. |
| G3 | Red | No explicit resumption logic for the skill itself. If the skill workflow is interrupted, the agent must infer how to resume. |
| G4 | Green | Reuses existing config and reports. |
| G5 | Green | Report schema is documented. |
| G6 | Green | Freshness rules are documented. |
| G7 | Green | Missing optional reports are handled gracefully. |

### H. Delegation and scripts

| Id | Rating | Notes |
|---|---|---|
| H1 | Green | Subagents are appropriate for the distinct tasks (scope, method, capture, context). |
| H2 | Green | Worker boundaries are clear. |
| H3 | Green | Workers reference the standard return contract. |
| H4 | Green | Workers return `needs_input` to the conductor. |
| H5 | Green | Deterministic logic lives in `scripts/`. |
| H6 | Green | Scripts are read-only and safe. |

### I. Reusability and composition

| Id | Rating | Notes |
|---|---|---|
| I1 | Green | Dependencies and consumed reports are declared. |
| I2 | N/A | No obvious shared conventions to extract. |
| I3 | Green | Handles absence of optional reports gracefully. |
| I4 | Green | Method detection and selection follow one consistent pattern. |
| I5 | Green | No premature abstraction. |

### J. Security

| Id | Rating | Notes |
|---|---|---|
| J1 | Green | No secrets in skill files. |
| J2 | Green | Branch switching and overwrites are confirmed. |
| J3 | Green | External tools (MCPs, browsers) are documented. |
| J4 | Green | Read-only investigation preferred. |
| J5 | Green | Writes limited to `.agents/context/` and `.agents/config/`. |

### K. Evaluation and lifecycle

| Id | Rating | Notes |
|---|---|---|
| K1 | Red | No trigger evals documented. |
| K2 | Red | No behavior evals documented. |
| K3 | Green | Version is declared in frontmatter and report schema. |
| K4 | N/A | Migration path not needed for first review. |
| K5 | Red | No maintenance or review plan. |

## Inconsistencies found

1. **Report version mismatch.** `SKILL.md` frontmatter says `version: "3.0"`, `CONTEXT_REPORTS.md` says reports should use `version: 3`, but `EXAMPLES.md` uses `version: 1` and `ticket:` instead of `scope:`.
2. **Field naming inconsistency.** `EXAMPLES.md` uses `ticket` while `CONTEXT_REPORTS.md` uses `scope`. This is documented as a migration case, but the examples should still use the current schema.
3. **Skill type mismatch.** Declared as "Workflow skill", but the standard types are standalone, building-block, conductor, hybrid. The skill is best described as a hybrid or conductor because it delegates to subagents.

## Blockers (Red on principle criteria)

1. **A3** — No leading word front-loaded.
2. **A4** — Invocation mode not declared.
3. **C2** — Steps in SKILL.md lack completion criteria.
4. **E1** — Scope not declared.
5. **G3** — No resumption logic.
6. **K1, K2, K5** — No evals or maintenance plan.

## Positive findings

- Strong progressive disclosure: SKILL.md is the overview, references hold detail.
- Good worker boundaries and return contracts.
- Method detection is project-type driven and agnostic.
- Security handling is sound (no secrets, session files, env-var references).
- Config pattern is well-documented and respects user preferences.
- Reports have a clear schema and freshness rules.

## Recommended redesign direction

1. **Add explicit frontmatter**: `scope: global`, `invocation: user-invoked`, `disable-model-invocation: true`.
2. **Front-load a leading word**: rewrite the description to start with "Capture" or "Baseline" and use it as the anchor throughout.
3. **Correct skill type**: declare as **hybrid** or **conductor** (likely hybrid because it has a clear workflow but also delegates to workers).
4. **Add completion criteria to the Process overview steps** in `SKILL.md`, or move the detailed workflow entirely into `references/WORKFLOW.md` and keep only the high-level skeleton in `SKILL.md`.
5. **Add resumption logic**: document what state files exist and how to resume if interrupted.
6. **Fix inconsistencies**: update `EXAMPLES.md` to use `version: 3` and `scope:` instead of `ticket:`.
7. **Add a minimal evaluation plan**: trigger evals, behavior evals, review cadence.
8. **Consider making `SKILL.md` leaner** by moving `Quick start`, `Optional context consumption`, `Branch and commit tracking`, `Report location`, and `Output formats` into references or README, keeping only the core contract in `SKILL.md`.

## Verdict

`baseline` is a well-structured, functional skill with good progressive disclosure and sound security. However, it lacks explicit invocation/scope declarations, a leading word, completion criteria, and resumption logic. It also has schema inconsistencies between documentation and examples. The recommended changes are moderate and would bring it into alignment with the skill fundamentals without changing its core behavior.
