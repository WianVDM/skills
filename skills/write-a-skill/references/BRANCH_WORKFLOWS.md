# Branch workflows

This reference holds the detailed step-by-step workflows for each `write-a-skill` branch. `SKILL.md` keeps only the branch summary and completion criterion; reach this file when the conductor needs the full phase list for a branch.

## New skill workflow

### 1. Clarify intent

**Why this phase exists:** Designing the wrong skill is expensive. Clarifying intent first prevents building a solution for the wrong problem.

Understand the problem, trigger, success criteria, and whether a skill is warranted. Use grill-me-style questions with proposed defaults.

**Completion criterion:** the intent note contains the problem, trigger, success criteria, and a yes/no/maybe verdict on whether a skill is warranted.

### 2. Classify the skill

**Why this phase exists:** The shape of the skill (type, invocation, portability, autonomy) determines every later decision.

Determine the skill type, invocation mode, portability target, core objective, boundaries, and autonomy level.

**Completion criterion:** the design doc records the skill type, invocation mode, portability target, core objective, in-scope items, out-of-scope items, and autonomy level.

### 3. Explore alternatives

**Why this phase exists:** A new skill should be the last resort, not the first. Existing skills, scripts, MCP servers, or prompt templates often solve the problem with less maintenance.

Before committing, check whether an existing skill, tool, MCP server, extension, prompt template, or script already solves the problem.

**Completion criterion:** the alternatives report lists existing options and gives a clear recommendation: build new skill, reuse/extend existing skill, or use an alternative.

### 4. Design the skill

**Why this phase exists:** A confirmed design is the contract that prevents scope creep, hidden assumptions, and bloated drafts.

Produce a structured design covering objective, boundaries, skill type, portability, config, context interface, delegation, scripts, state, security, and directory structure.

**Completion criterion:** the design doc covers every section in the design template and contains no unresolved blockers.

### 5. Curate scripts

**Why this phase exists:** Deterministic logic belongs in scripts, not in AI inference. This phase forces the design to distinguish judgment from repeatable computation.

Identify where repeatable, deterministic logic should live in scripts rather than AI inference. Propose inputs, outputs, and failure behavior.

**Completion criterion:** a scripts plan exists that lists every proposed script, or explicitly states that no scripts are needed.

### 6. Assess global readiness

**Why this phase exists:** A project-specific skill is fine, but the design should know what it would cost to make it global, even if it never is.

If the skill is project-specific, identify what blocks it from being global and what remediation would take.

**Completion criterion:** the global readiness report lists project-specific assumptions, missing dependency declarations, and remediation steps with effort estimates.

### 7. Self-audit against fundamentals

**Why this phase exists:** The conductor should catch principle violations before the user sees the design, not after.

Challenge the design for over-complication and principle violations before showing it to the user.

**Completion criterion:** the design passes every check in [references/SELF_AUDIT_CHECKLIST.md](references/SELF_AUDIT_CHECKLIST.md), or the user explicitly overrides a failed check with a recorded reason.

### 8. Confirm with the user

**Why this phase exists:** Drafting files without approval is the most common destructive action in this skill. This gate makes it explicit.

Present the design, audit, and alternatives summary. Do not proceed to implementation until the user confirms or revises.

**Completion criterion:** the user has explicitly approved the design or provided a revised version that passes the self-audit.

### 9. Draft the skill

**Why this phase exists:** Only after the design is approved does the skill produce concrete files. Drafting is the execution of the design, not the design itself.

Once confirmed, write the skill files: `SKILL.md`, `README.md`, references, subagents, scripts, and assets/templates.

**Completion criterion:** all files in the approved design are created and the directory structure matches the design.

### 10. Validate and close

**Why this phase exists:** The design may pass, but the drafted files can still drift. A final audit closes the loop.

Run a final audit against the rubric, capture any remaining gaps, and ask the user whether to iterate or finish.

**Completion criterion:** a final review report exists and the user has chosen to iterate or close.

## Quick skill workflow

A compressed version of the New workflow for minimal skills.

1. **Clarify intent** (minimal) — capture problem, trigger, and success criteria.  
   *Why:* Even a quick skill needs a clear problem before it can be designed.
2. **Classify** — choose type, invocation, portability, and objective.  
   *Why:* The shape of the skill still determines its files and dependencies.
3. **Explore alternatives** (light) — check existing skills and simple alternatives.  
   *Why:* A quick skill should not be created if a script or template suffices.
4. **Design** (light) — produce a minimal design doc.  
   *Why:* The design is the contract, even for a small skill.
5. **Self-audit** — run the fundamentals checklist.  
   *Why:* Small skills are still bound by the principles.
6. **Confirm** — present the design and audit before drafting.  
   *Why:* No drafting without explicit approval.
7. **Draft** — write the skill files.  
   *Why:* Execution of the approved design.
8. **Validate** — final audit and close.  
   *Why:* Close the loop and capture any gaps.

## Review workflow

1. **Read the skill** — load `SKILL.md`, `README.md`, references, subagents, scripts, and assets.  
   *Why:* An audit is only as good as the files it reads.
2. **Classify the skill** — determine its type, form, and portability target.  
   *Why:* The audit rubric applies differently depending on the skill type.
3. **Audit against the rubric** — evaluate against [references/AUDIT_RUBRIC.md](references/AUDIT_RUBRIC.md).  
   *Why:* The rubric is the single canonical standard.
4. **Produce a report** — ratings per category, positive findings, issues, and optional refactor/upgrade path.  
   *Why:* The user needs a structured, actionable report.

**Completion criterion:** the audit report is complete, structured, and references the rubric criteria by id.

## Upgrade workflow

1. **Read the skill** — load existing files.  
   *Why:* The upgrade plan must be grounded in the actual files.
2. **Identify project-specific assumptions** — hardcoded paths, tool names, APIs, conventions, implicit dependencies.  
   *Why:* These are the blockers to global portability.
3. **Identify missing dependency declarations** — required tools, skills, env vars, etc.  
   *Why:* Global skills must declare everything they need.
4. **Propose remediation** — concrete steps with effort estimates to make the skill global-ready.  
   *Why:* The user decides what cost is worth paying.
5. **Confirm before applying** — present the plan; apply changes only after explicit approval.  
   *Why:* Upgrading modifies existing files, so it is a destructive action.

**Completion criterion:** a remediation plan exists and the user has approved or declined each proposed change.
