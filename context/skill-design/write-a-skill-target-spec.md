# Target specification for `write-a-skill`

> Temporary design document. When this is finalized, it becomes the audit criteria `write-a-skill` will use to review itself and other skills.

---

## 1. Purpose

`write-a-skill` is a **user-invoked, global, pluggable conductor skill** that helps anyone design, draft, review, or upgrade an agent skill according to the `skill-standards` fundamentals.

It acts as a **design partner with a spine**: it is relentless in understanding what the user wants, proposes strong defaults, and can oppose the user when a choice violates a fundamental principle. It favors simplicity and always asks before imposing assumptions.

---

## 2. Invocation and portability

- **Invocation mode:** user-invoked. The skill is a meta-design conversation. It should not stay loaded in the agent's context window during normal work, and no other skill should reach it autonomously.
- **Declaration:** `invocation: user-invoked` and `disable-model-invocation: true` should both appear in `SKILL.md` frontmatter so the mode is unambiguous across harnesses.
- **Portability target:** global. It must work in any project with any agent harness.
- **Pluggable behavior:** It detects `.agents/`, `skills/`, and `context/` directories but **always confirms** with the user before writing files. If detection is ambiguous, it asks.
- **No hardcoded project paths:** Paths must be resolved through detection or user confirmation.

---

## 3. Entry branches

The user invokes `write-a-skill` and the conductor classifies intent into one branch. Each branch has its own sequence and artifact set. Detailed branch workflows may be disclosed in `references/BRANCH_WORKFLOWS.md`; keep in `SKILL.md` only the branch summary, completion criterion, and the pointer.

| Branch | Trigger | Outcome |
|---|---|---|
| **New** | User wants to design a new skill from scratch. | Full design workflow + draft. |
| **Quick** | User wants a minimal skill based on a brief description. | Lightweight design workflow + draft. |
| **Review** | User wants to audit an existing skill. | Audit report with ratings. |
| **Upgrade** | User wants to make a project-specific skill global-ready. | Remediation plan + optional changes. |

If the user's intent is unclear, the conductor asks a single clarifying question with a proposed default.

---

## 4. Core workflows

### 4.1 New skill workflow

1. **Clarify intent.** Ask `grill-me`-style questions with proposed defaults. Capture the problem, trigger, success criteria, and whether a skill is even warranted.
2. **Classify.** Choose skill type, invocation mode, portability target, and autonomy level.
3. **Explore alternatives.** Check if a script, MCP server, extension, prompt template, or existing skill solves the problem better.
4. **Design.** Propose structure, form, config, context interface, delegation, scripts, state, and security.
5. **Simplicity check.** Challenge the design: *"Do we need this?"*, *"Can this be simpler?"*, *"Is this a hidden building block?"*
6. **Self-audit.** Run the proposed design against the fundamentals with a lightweight pass.
7. **Confirm.** Present the design and audit. Do not draft until the user confirms or revises.
8. **Draft.** Write the skill files.
9. **Validate.** Run a final audit and optionally produce eval prompts.

### 4.2 Quick skill workflow

A compressed version of the New workflow. It skips deep design but still runs a lightweight self-audit and confirms the draft before writing.

### 4.3 Review workflow

1. Read the existing skill files.
2. Classify the skill type and form.
3. Audit the skill against the audit criteria in Section 6.
4. Produce a report with ratings per category, positive findings, and issues.
5. Optionally propose a refactor or upgrade path.

### 4.4 Upgrade workflow

1. Read the existing skill files.
2. Identify project-specific assumptions: hardcoded paths, tool names, APIs, conventions.
3. Identify missing dependency declarations.
4. Propose concrete remediation steps with effort estimates.
5. Confirm with the user before applying changes.

---

## 5. Design principles the skill enforces

These are non-negotiable. The skill should block the user from proceeding until these are satisfied.

- **One core objective.** A skill owns exactly one problem domain.
- **Explicit out-of-scope.** The skill must declare what it does not do.
- **Explicit dependencies.** Required tools, APIs, MCP servers, skills, and environment variables must be declared.
- **No secrets in files.** Secrets must be referenced via environment variables or secure stores.
- **Destructive actions confirmed.** Any mutation requires explicit user confirmation.
- **Harness-agnostic and project-agnostic language** for global skills.
- **No hidden assumptions.** Global skills must declare all assumptions and fail closed when required capabilities are missing.
- **Appropriate skill type.** The type must match the shape of the problem.

---

## 6. Audit criteria (the rating rubric)

This is the rubric `write-a-skill` will use to review other skills and, eventually, itself.

Each criterion is rated on a simple scale:

- **Green** — meets the standard.
- **Yellow** — meets the standard but could be improved.
- **Red** — violates the standard and should be fixed.
- **N/A** — not applicable to this skill.

A **Red** on any principle criterion (marked with 🔒) is a blocker.

### A. Identity and invocation

- **A1. Name.** Lowercase, hyphen-separated, matches directory name.
- **A2. Description.** Under 1024 characters, states what the skill does and when to use it, with trigger keywords. 🔒
- **A3. Description as context pointer.** Front-loads the leading word or domain; one trigger per branch; no duplicate triggers. 🔒
- **A4. Invocation mode.** Explicitly chosen as model-invoked or user-invoked; declared in `SKILL.md` frontmatter via `invocation` and/or `disable-model-invocation`; matches actual behavior. 🔒

### B. Objective and scope

- **B1. One core objective.** The skill owns one problem domain. 🔒
- **B2. Clear purpose.** `SKILL.md` states what the skill does and the outcome it produces.
- **B3. Clear when to use.** Lists realistic triggers.
- **B4. Out of scope.** Explicitly declares what is not handled. 🔒
- **B5. Right skill type.** Type matches the problem: standalone, building-block, conductor, or hybrid. 🔒

### C. Form and style

- **C1. Form matches domain.** Instruction-heavy, guideline-heavy, or hybrid; chosen for the right reason. 🔒
- **C2. Steps have completion criteria.** Every step ends with a checkable condition. 🔒
- **C3. Completion criteria are strong.** Checkable and exhaustive where it matters.
- **C4. Leading words used.** Where the agent's priors are strong, a compact leading word anchors behavior.
- **C5. Explain-the-why.** Rules explain reasoning, not just issue commands.
- **C6. Negation pairs.** Every "do not X" is paired with a positive directive.
- **C7. No vague guideline soup.** True statements are paired with specific principles, leading words, or criteria. 🔒
- **C8. No manual in disguise.** Intent is stated, not mechanics. 🔒
- **C9. No hidden hybrid.** Steps and guidelines are clearly separated.
- **C10. No no-op lines.** Every line changes behavior versus the default or is removed. 🔒

### D. Information hierarchy and structure

- **D1. Progressive disclosure.** Detail lives at the right level: `SKILL.md` for what every path needs, `references/` for disclosed detail, external reference for shared material. 🔒
- **D2. Co-location.** Related concepts are grouped under one heading.
- **D3. No sprawl.** `SKILL.md` is lean; excess is pushed down the hierarchy or split. 🔒
- **D4. No sediment.** Stale guidance has been removed. 🔒
- **D5. No duplication.** Each meaning lives in one authoritative place. 🔒
- **D6. Required files present.** `SKILL.md` exists; `README.md` for non-trivial skills.
- **D7. No empty directories.** Optional directories contain content.
- **D8. Reference links resolve.** All links point to existing files.
- **D9. Flat structure.** Avoids deep nesting.

### E. Global vs project-specific

- **E1. Pluggability declared.** The skill states whether it is global or project-specific. 🔒
- **E2. Harness-agnostic language.** No harness-specific tool names, slash commands, or vendor APIs. 🔒 for global skills.
- **E3. Project-agnostic language.** No hardcoded project tools, paths, or APIs. 🔒 for global skills.
- **E4. Detection before config.** Environment is detected before asking the user.
- **E5. Dependencies declared.** All required skills, tools, APIs, and environment variables are listed. 🔒
- **E6. Fail closed.** Missing required capabilities stop the skill with a clear explanation. 🔒

### F. Configuration

- **F1. Config schema documented.** If configurable, keys and defaults are documented.
- **F2. No secrets in config.** Secrets are referenced via env vars, not stored. 🔒
- **F3. No over-configuring.** Config is persisted only for choices that change future behavior.
- **F4. Notes are memory.** Notes change how future invocations behave; logs are not notes.
- **F5. Never overwrite without asking.** Existing config represents user decisions. 🔒

### G. State and context

- **G1. State location documented.** If stateful, the skill documents where state lives. 🔒
- **G2. State schema documented.** Frontmatter and body structure are predictable. 🔒
- **G3. Resumption logic.** After context compaction, the skill can resume from state without guessing. 🔒
- **G4. No duplicate work.** Re-runs reuse completed state instead of overwriting.
- **G5. Report schema documented.** Produced reports include skill, version, key, timestamp, and summary. 🔒
- **G6. Freshness handled.** Consumers check timestamps and underlying changes before relying on reports.
- **G7. Missing reports handled.** No silent failures; required missing reports trigger consultation or an approved fallback. 🔒

### H. Delegation and scripts

- **H1. Delegation is appropriate.** Workers are used for large, isolated, or cross-cutting tasks; not for trivial work. 🔒
- **H2. Worker boundaries clear.** Each worker prompt states role, scope, tools, forbidden actions, and return format. 🔒
- **H3. Worker return contract.** Structured return format is defined and referenced. 🔒
- **H4. Workers do not ask users.** They return `needs_input` to the conductor. 🔒
- **H5. Scripts for deterministic logic.** Repeatable, stable logic lives in scripts, not `SKILL.md`. 🔒
- **H6. Scripts are safe and isolated.** Documented, deterministic, no destructive actions, no user input. 🔒

### I. Reusability and composition

- **I1. Dependencies declared.** Required skills and consumed reports are listed. 🔒
- **I2. Building-block extraction.** Shared conventions are extracted rather than duplicated. 🔒
- **I3. Consumers handle absence gracefully.** Missing dependencies are noted or consulted, not silently ignored. 🔒
- **I4. One-way pattern consistency.** Each recurring problem has one canonical default approach. 🔒
- **I5. No premature abstraction.** Building blocks are extracted only when reused or clearly reusable. 🔒

### J. Security

- **J1. No secrets in skill files.** 🔒
- **J2. Destructive actions confirmed.** 🔒
- **J3. External access documented.** APIs, MCP servers, and extensions are declared. 🔒
- **J4. Read-only investigation preferred.** 🔒
- **J5. Safe in untrusted projects by default.** 🔒

### K. Evaluation and lifecycle

- **K1. Description tested.** Trigger evals exist or are planned. 🔒
- **K2. Behavior tested.** With-skill and baseline runs are planned or documented. 🔒
- **K3. Versioned.** Version is bumped when schema, config, or behavior changes significantly. 🔒
- **K4. Migration path.** Breaking changes document how stale reports or config are handled. 🔒
- **K5. Maintenance plan.** The skill is scheduled for review after real-world usage. 🔒

---

## 7. Decision rules

When the user proposes a design that conflicts with the fundamentals:

- **Block** on principle violations. Explain the principle, why it matters, and offer a concrete alternative.
- **Warn** on preference choices. Explain the trade-off and recommend a default.
- **Ask** when assumptions are required. Present detected options and let the user choose.
- **Confirm** before destructive actions. This includes drafting files, overwriting config, or modifying existing skills.

The skill should never proceed on a guess about user intent.

---

## 8. Artifact surface

Keep the artifact surface minimal to avoid cognitive overload:

- `.agents/context/skill-design/{skill-name}-intent.md` — captured user intent and constraints.
- `.agents/context/skill-design/{skill-name}-design.md` — proposed design.
- `.agents/context/skill-review/{skill-name}-audit.md` — self-audit or review report.
- `.agents/context/skill-design/{skill-name}-decisions.md` — decision log.
- Final skill files in `.agents/skills/{skill-name}/` or the detected/confirmed skills directory.

For quick mode, only the design doc and final files are required.

---

## 9. Self-audit rules

Before presenting any design to the user, the conductor must run a lightweight self-audit:

- Check that the proposed skill has one core objective.
- Check that dependencies are declared.
- Check that the form matches the domain.
- Check that steps have completion criteria.
- Check that the description is trigger-rich and not duplicated.
- Check that no secrets are hardcoded.
- Check that global skills are project-agnostic and harness-agnostic.
- Check that the design is not over-complicated for the stated problem.

If the self-audit fails, the conductor must fix the design or escalate to the user before drafting.

---

## 10. Anti-over-complication checks

The skill must challenge itself and the user at every step:

- Does this need to be a skill, or could a script, MCP server, or prompt template solve it?
- Does this skill need all proposed features, or can the first version be smaller?
- Are proposed building blocks actually reusable, or are they premature abstraction?
- Does the skill need state, or can it be stateless?
- Does it need config, or can it detect everything?
- Does it need to delegate, or is the work small enough to do inline?

These checks prevent the conductor from producing a bloated skill when a simple one would suffice.
