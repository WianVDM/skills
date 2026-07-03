# Audit rubric

This is the rubric `write-a-skill` uses to review skills and to audit itself. Each criterion is rated on a four-point scale:

- **Green** — meets the standard.
- **Yellow** — meets the standard but could be improved.
- **Red** — violates the standard and should be fixed.
- **N/A** — not applicable to this skill.

A **Red** on any principle criterion (marked with 🔒) is a blocker.

## A. Identity and invocation

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| A1 | Name is lowercase, hyphen-separated, and matches the directory name. | | |
| A2 | Description is under 1024 characters, states what the skill does, and lists trigger keywords. | 🔒 | |
| A3 | Description front-loads the leading word or domain; one trigger per branch; no duplicate triggers. | 🔒 | |
| A4 | Invocation mode is explicitly declared as `model-invoked` or `user-invoked`, and matches actual behavior. | 🔒 | |

## B. Objective and scope

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| B1 | One core objective. The skill owns one problem domain. | 🔒 | |
| B2 | Clear purpose. `SKILL.md` states what the skill does and the outcome it produces. | | |
| B3 | Clear when to use. Realistic triggers are listed. | | |
| B4 | Explicit out-of-scope. The skill declares what it does not handle. | 🔒 | |
| B5 | Right skill type. The type matches the problem: standalone, building-block, conductor, or hybrid. | 🔒 | |

## C. Form and style

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| C1 | Form matches domain. Instruction-heavy, guideline-heavy, or hybrid; chosen for the right reason. | 🔒 | |
| C2 | Steps have completion criteria. Every step ends with a checkable condition. | 🔒 | |
| C3 | Completion criteria are strong. Checkable and exhaustive where it matters. | | |
| C4 | Leading words are used. A compact leading word anchors behavior where the agent's priors are strong. | | |
| C5 | Explain-the-why. Rules explain reasoning, not just issue commands. | | |
| C6 | Negation pairs. Every "do not X" is paired with a positive directive. | | |
| C7 | No vague guideline soup. True statements are paired with specific principles, leading words, or criteria. | 🔒 | |
| C8 | No manual in disguise. Intent is stated, not mechanics. | 🔒 | |
| C9 | No hidden hybrid. Steps and guidelines are clearly separated. | | |
| C10 | No no-op lines. Every line changes behavior versus the default or is removed. | 🔒 | |

## D. Information hierarchy and structure

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| D1 | Progressive disclosure. Detail lives at the right level: `SKILL.md` for what every path needs, `references/` for disclosed detail, external reference for shared material. | 🔒 | |
| D2 | Co-location. Related concepts are grouped under one heading. | | |
| D3 | No sprawl. `SKILL.md` is lean; excess is pushed down the hierarchy or split. | 🔒 | |
| D4 | No sediment. Stale guidance has been removed. | 🔒 | |
| D5 | No duplication. Each meaning lives in one authoritative place. | 🔒 | |
| D6 | Required files present. `SKILL.md` exists; `README.md` for non-trivial skills. | | |
| D7 | No empty directories. Optional directories contain content. | | |
| D8 | Reference links resolve. All links point to existing files. | | |
| D9 | Flat structure. Avoids deep nesting. | | |

## E. Global vs project-specific

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| E1 | Pluggability declared. The skill states whether it is global or project-specific. | 🔒 | |
| E2 | Harness-agnostic language. No harness-specific tool names, slash commands, or vendor APIs. | 🔒 | For global skills. |
| E3 | Project-agnostic language. No hardcoded project tools, paths, or APIs. | 🔒 | For global skills. |
| E4 | Detection before config. The environment is detected before asking the user. | | |
| E5 | Dependencies declared. All required skills, tools, APIs, and environment variables are listed. | 🔒 | |
| E6 | Fail closed. Missing required capabilities stop the skill with a clear explanation. | 🔒 | |

## F. Configuration

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| F1 | Config schema documented. If configurable, keys and defaults are documented. | | |
| F2 | No secrets in config. Secrets are referenced via env vars, not stored. | 🔒 | |
| F3 | No over-configuring. Config is persisted only for choices that change future behavior. | | |
| F4 | Notes are memory. Notes change how future invocations behave; logs are not notes. | | |
| F5 | Never overwrite without asking. Existing config represents user decisions. | 🔒 | |

## G. State and context

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| G1 | State location documented. If stateful, the skill documents where state lives. | 🔒 | |
| G2 | State schema documented. Frontmatter and body structure are predictable. | 🔒 | |
| G3 | Resumption logic. After context compaction, the skill can resume from state without guessing. | 🔒 | |
| G4 | No duplicate work. Re-runs reuse completed state instead of overwriting. | | |
| G5 | Report schema documented. Produced reports include skill, version, key, timestamp, and summary. | 🔒 | |
| G6 | Freshness handled. Consumers check timestamps and underlying changes before relying on reports. | | |
| G7 | Missing reports handled. No silent failures; required missing reports trigger consultation or an approved fallback. | 🔒 | |

## H. Delegation and scripts

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| H1 | Delegation is appropriate. Workers are used for large, isolated, or cross-cutting tasks; not for trivial work. | 🔒 | |
| H2 | Worker boundaries clear. Each worker prompt states role, scope, tools, forbidden actions, and return format. | 🔒 | |
| H3 | Worker return contract. Structured return format is defined and referenced. | 🔒 | |
| H4 | Workers do not ask users. They return `needs_input` to the conductor. | 🔒 | |
| H5 | Scripts for deterministic logic. Repeatable, stable logic lives in scripts, not `SKILL.md`. | 🔒 | |
| H6 | Scripts are safe and isolated. Documented, deterministic, no destructive actions, no user input. | 🔒 | |

## I. Reusability and composition

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| I1 | Dependencies declared. Required skills and consumed reports are listed. | 🔒 | |
| I2 | Building-block extraction. Shared conventions are extracted rather than duplicated. | 🔒 | |
| I3 | Consumers handle absence gracefully. Missing dependencies are noted or consulted, not silently ignored. | 🔒 | |
| I4 | One-way pattern consistency. Each recurring problem has one canonical default approach. | 🔒 | |
| I5 | No premature abstraction. Building blocks are extracted only when reused or clearly reusable. | 🔒 | |

## J. Security

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| J1 | No secrets in skill files. | 🔒 | |
| J2 | Destructive actions confirmed. | 🔒 | |
| J3 | External access documented. APIs, MCP servers, and extensions are declared. | 🔒 | |
| J4 | Read-only investigation preferred. | 🔒 | |
| J5 | Safe in untrusted projects by default. | 🔒 | |

## K. Evaluation and lifecycle

| Id | Criterion | 🔒 | Notes |
|---|---|---|---|
| K1 | Description tested. Trigger evals exist or are planned. | 🔒 | |
| K2 | Behavior tested. With-skill and baseline runs are planned or documented. | 🔒 | |
| K3 | Versioned. Version is bumped when schema, config, or behavior changes significantly. | 🔒 | |
| K4 | Migration path. Breaking changes document how stale reports or config are handled. | 🔒 | |
| K5 | Maintenance plan. The skill is scheduled for review after real-world usage. | 🔒 | |

## Reporting format

When producing an audit report, list findings as:

```markdown
| Criterion | Rating | Notes |
|---|---|---|
| A2 | Red | Description exceeds 1024 characters. |
```

For each red or yellow finding, include:

- The criterion id.
- The specific observation.
- A concrete recommendation.
- Whether the issue is a blocker (🔒).
