---
skill: handoff
version: "1.0"
timestamp: 2026-07-03T00:00:00Z
auditor: write-a-skill
scope: global
---

# Handoff skill audit

## Classification

| Attribute | Current value | Assessment |
|---|---|---|
| Type | Standalone | Plausible, but it leans toward hybrid because it consumes other reports (verify-branch) and suggests follow-on skills. |
| Invocation | Implicitly user-invoked | Not declared in frontmatter. Must be explicit. |
| Portability target | Global | Intended as global, but contains harness-specific and project-specific assumptions. |
| Core objective | Write a handoff document summarising the current conversation. | Clear and singular. |
| Leading word | Missing | Needs a compact verb (e.g., “Capture”, “Summarize”) to anchor behavior. |

## Audit findings

### A. Identity and invocation

| Id | Rating | Notes |
|---|---|---|
| A1 | Green | Name matches directory, lowercase, hyphen-separated. |
| A2 | Yellow | Description lists triggers but buries them in a feature sentence. “Supports persistent checkpoints” is not a trigger. |
| A3 | Red | No leading word front-loaded. Multiple trigger phrases are crammed together. |
| A4 | Red | `invocation` and `disable-model-invocation` are not declared in frontmatter. |

### B. Objective and scope

| Id | Rating | Notes |
|---|---|---|
| B1 | Green | One core objective: produce a handoff document. |
| B2 | Green | Purpose is clear in the first paragraph. |
| B3 | Yellow | Triggers live only in description; body should explicitly restate them. |
| B4 | Red | No out-of-scope declaration. |
| B5 | Yellow | Could be standalone, but the verify-branch integration and skill-suggestion hint at composition/conductor behavior. |

### C. Form and style

| Id | Rating | Notes |
|---|---|---|
| C1 | Yellow | Instruction-heavy but lacks completion criteria. Form is not explicitly chosen. |
| C2 | Red | No steps with completion criteria. |
| C3 | N/A | No completion criteria to evaluate. |
| C4 | Red | No leading word anchors agent behavior. |
| C5 | Yellow | “Do not duplicate content” does not explain why. |
| C6 | Red | “Do not duplicate content” lacks a paired positive directive. |
| C7 | Yellow | “Suggest the skills to be used, if any” is vague guideline soup. |
| C8 | Yellow | Mix of intent and mechanics. |
| C9 | Green | No hidden hybrid; mostly instructions. |
| C10 | Green | Each line changes behavior. |

### D. Information hierarchy and structure

| Id | Rating | Notes |
|---|---|---|
| D1 | Green | Simple skill; no excess detail that needs pushing down. |
| D2 | Green | Related concepts are grouped. |
| D3 | Green | SKILL.md is lean. |
| D4 | Green | No stale guidance detected. |
| D5 | Green | No duplication. |
| D6 | Yellow | No README.md. |
| D7 | N/A | No directories to check. |
| D8 | N/A | No internal links. |
| D9 | Green | Flat structure. |

### E. Global vs project-specific

| Id | Rating | Notes |
|---|---|---|
| E1 | Red | Scope is not declared in frontmatter. |
| E2 | Red | Uses `/handoff` slash-command syntax, which is harness-specific. |
| E3 | Yellow | Hardcodes `.handoff/` and uses `mktemp` without detection. |
| E4 | N/A | No configurable values, but environment could be detected. |
| E5 | Red | Required capabilities (filesystem, mktemp, git branch detection, report reading) are not declared. |
| E6 | Red | Does not fail closed when required capabilities are missing. |

### F. Configuration

| Id | Rating | Notes |
|---|---|---|
| F1 | N/A | No configurable keys. |
| F2 | Green | No secrets. |
| F3 | N/A | No persistent config. |
| F4 | N/A | No notes. |
| F5 | Red | No rule for overwriting an existing checkpoint. |

### G. State and context

| Id | Rating | Notes |
|---|---|---|
| G1 | Yellow | Paths are mentioned but not explicitly framed as state/output locations. |
| G2 | Red | No schema for the handoff document. |
| G3 | Red | No resumption logic for the handoff skill itself. |
| G4 | N/A | No multi-step state to reuse. |
| G5 | Red | No report schema for the produced handoff document. |
| G6 | N/A | Not applicable. |
| G7 | N/A | Not applicable. |

### H. Delegation and scripts

| Id | Rating | Notes |
|---|---|---|
| H1 | Green | No delegation needed; scope is small enough for inline execution. |
| H2 | N/A | No workers. |
| H3 | N/A | No workers. |
| H4 | N/A | No workers. |
| H5 | Red | Ticket-key parsing, path selection, and verify-branch detection are deterministic and should be scripted. |
| H6 | N/A | No scripts. |

### I. Reusability and composition

| Id | Rating | Notes |
|---|---|---|
| I1 | Red | Required skills/tools/reports not declared. |
| I2 | N/A | No shared conventions to extract. |
| I3 | N/A | No consumers. |
| I4 | N/A | No recurring pattern to canonicalize. |
| I5 | N/A | No premature abstraction. |

### J. Security

| Id | Rating | Notes |
|---|---|---|
| J1 | Green | No secrets in skill files. |
| J2 | Red | Writing files and overwriting checkpoints are not gated by explicit confirmation. |
| J3 | Green | No external APIs. |
| J4 | N/A | Not a read-only skill. |
| J5 | Yellow | Writes files in untrusted projects without confirmation. |

### K. Evaluation and lifecycle

| Id | Rating | Notes |
|---|---|---|
| K1 | Red | No trigger evals. |
| K2 | Red | No behavior evals. |
| K3 | Red | No version in frontmatter. |
| K4 | N/A | First version; no migration needed yet. |
| K5 | Red | No maintenance or review plan. |

## Blockers (Red on principle criteria)

1. **A4** — Invocation mode not declared.
2. **A3** — No leading word / poor description structure.
3. **B4** — Missing out-of-scope.
4. **E1** — Scope not declared.
5. **E2** — Harness-specific syntax (`/handoff`).
6. **E5** — Dependencies not declared.
7. **E6** — Does not fail closed.
8. **F5** — Overwrite behavior undefined.
9. **G2** — No handoff document schema.
10. **G3** — No resumption logic.
11. **G5** — No report schema.
12. **H5** — Deterministic logic not in scripts.
13. **I1** — Dependencies not declared.
14. **J2** — Destructive writes not confirmed.
15. **K1, K2, K3, K5** — No evals, version, or maintenance plan.

## Positive findings

- Core objective is singular and easy to understand.
- SKILL.md is short and avoids sprawl.
- It already distinguishes default vs. persistent modes.
- It references existing artifacts by path instead of duplicating them.
- It already integrates a useful cross-skill report (verify-branch findings).

## Recommended redesign path

1. **Add explicit frontmatter** with `version`, `scope: global`, `invocation: user-invoked`, `disable-model-invocation: true`, and `metadata`.
2. **Rewrite the description** to front-load a leading word (e.g., “Capture”) and list one trigger per branch.
3. **Add an out-of-scope section** (e.g., does not create tickets, does not run tests, does not modify code).
4. **Add a dependencies section** (filesystem, mktemp, git branch detection, optional verify-branch report).
5. **Add structured steps with completion criteria**, e.g.:
   - Collect context → all referenced artifacts are listed by path.
   - Resolve output path → path exists and user confirms overwrite if needed.
   - Draft handoff → document follows the schema.
   - Persist → file is written and path is reported to the user.
6. **Define the handoff document schema** (frontmatter + body sections: current focus, decisions made, open questions, next actions, referenced artifacts, recommended skills, branch report summary).
7. **Add a deterministic script** for ticket-key extraction, path selection, and verify-branch report detection.
8. **Add overwrite confirmation** and a fail-closed rule when required capabilities are missing.
9. **Add a README.md** with usage examples and maintenance plan.
10. **Add a simple evaluation checklist** (trigger evals, behavior evals, review cadence).
