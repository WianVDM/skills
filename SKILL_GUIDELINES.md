---
title: Agent Skill Design Guidelines
draft: true
---

# Agent Skill Design Guidelines

These guidelines define what an agent skill is, how it should be structured, and what standards it must meet. They are grounded in the principles from [agentskills.io](https://agentskills.io/) and extend them with conventions for portability, modularity, composition, delegation, shared context, configuration, and self-improvement.

Use this document when creating, refactoring, or reviewing skills.

A skill is **not a script or manual** for the agent to execute word for word. It is a **compact operating philosophy** for a specific domain. The agent reads it, understands the objective, the boundaries, and the conventions, then reasons outward from there.

> **Distinction:** These guidelines use precise standards and policies for skill authors. The skills you write should still read as guidelines for the agent — principles and intent — not as step-by-step instructions.

---

## 1. The core philosophy

A skill gives the agent:

- A clear **objective**.
- A set of **principles and patterns**.
- Clear **boundaries** for what is in and out of scope.
- Rules for **delegation**, **state**, **config**, and **composition**.

The agent decides the exact actions. The skill decides the shape of those actions.

---

## 2. What a skill must be

### 2.1 One core objective

A skill owns exactly one problem domain. If a skill starts solving multiple unrelated problems, split it.

Good examples:

- `debrief` — understand a ticket or task and build confidence in it.
- `baseline` — capture the current state of something.
- `verify-branch` — check whether changed code will pass CI gates.

Bad example:

- A skill that reviews code, generates tests, deploys, and writes release notes.

### 2.2 Guidelines, not instructions

Write principles and intent. Avoid step-by-step procedures or exact commands.

| Bad | Good |
|-----|------|
| Run `git status`, then `git diff`. | Start by understanding the current working state. Prefer the project's version control status command as the fastest way to do this. |
| Write the file to `.debrief/OC-4644.md`. | Produce a debrief report in the shared context directory, using the ticket key in the filename. |
| Call the `Agent` tool with `subagent_type: coder`. | Spawn a focused worker with a narrow scope and wait for its findings. |

### 2.3 Lean and direct

`SKILL.md` must be concise, decisive, and unambiguous. Deep detail belongs in `references/`, `scripts/`, `subagents/`, `assets/`, or state files.

If a section grows long, move it out.

### 2.4 Modular and composable

Skills should be built from smaller, reusable pieces:

- Shared reference files.
- Reusable subagent personas.
- Shared scripts.
- Smaller internal skills consumed by larger user-facing skills.

Avoid duplication across skills. If two skills need the same logic, extract it.

### 2.5 Delegate by default

A skill should ask:

> Is this sub-task focused enough, large enough, or isolated enough to hand to a worker?

If yes, delegate it to a subagent. The skill remains the conductor and integrator. Delegation prevents context bloat and keeps the main skill focused on decisions.

Delegation applies to:

- Using other skills.
- Running focused investigations.
- Testing specific features or subsets.
- Generating artifacts that the main skill will integrate.

A skill should not try to do everything itself.

### 2.6 Compose with other skills

Skills share context through a common filesystem and consume each other's outputs. A powerful skill is often a thin conductor that delegates to several smaller skills and integrates their findings.

Example: a high-level skill the user invokes may use `debrief`, `baseline`, `diagnose`, `plan-next`, and others through subagents, while the user only ever invokes the top-level skill.

---

## 3. Skill types

Most skills fall into one of three categories.

| Type | Purpose | Stateful | Config | Delegates |
|------|---------|----------|--------|-----------|
| **Guideline** | Encode conventions, style, or checklists. | No | Optional | No |
| **Workflow** | Execute a multi-step process with memory. | Yes | Often | Sometimes |
| **Conductor** | Coordinate other skills and workers. | Yes | Often | Heavily |

### 3.1 Guideline skill

- Stateless.
- No config required.
- Shapes how the agent thinks or writes.
- Examples: coding style, commit conventions, security review checklists.

### 3.2 Workflow skill

- Owns a process.
- Maintains state across invocations.
- Produces reports or artifacts.
- May delegate large sub-tasks, but does the core work itself.
- Examples: `debrief`, `baseline`, `pr-report`.

### 3.3 Conductor skill

- Does not do the work itself.
- Decides which skills or workers to invoke.
- Maintains shared state and integrates findings.
- Heavy use of subagent delegation.
- Examples: `orchestrate`.

### 3.4 Start simple

Not every skill needs to be stateful. Not every skill needs to delegate everything. A small, well-defined skill is often better than one that tries to do everything.

When in doubt, start as a guideline or workflow skill. Promote to a conductor only when the skill's main job becomes coordination.

---

## 4. Structure and progressive disclosure

A skill is a directory. The shape below is the conventional layout. Use only the directories and files that add value. A guideline skill may only need `SKILL.md` and `README.md`.

```
skill-name/
├── SKILL.md                 # required: identity, intent, core guidelines
├── README.md                # for human maintainers
├── references/              # deep detail, schemas, edge cases, examples
│   ├── REFERENCE.md
│   ├── CONFIG_PATTERN.md
│   ├── CONTEXT_REPORTS.md
│   ├── SUBAGENTS.md
│   ├── SECURITY.md
│   ├── VALIDATION.md
│   └── EXAMPLES.md
├── scripts/                 # deterministic helpers
├── subagents/               # worker personas for delegation
└── assets/                  # templates and static resources
```

Principles:

- `SKILL.md` is required.
- Include `README.md` for non-trivial skills.
- Optional directories should contain content; do not include empty ones.
- Prefer a flat structure; avoid deep nesting.
- Reference links must resolve.

---

## 5. Frontmatter and identity

A skill declares its identity in the frontmatter of `SKILL.md`. Example:

```yaml
---
name: skill-name
description: What this skill does and when to trigger it.
license: Proprietary
metadata:
  author: your-name
  version: "1.0"
---
```

### Naming conventions

- Skill names: lowercase, hyphen-separated. Example: `verify-branch`.
- Config keys: lowercase, snake_case. Group related keys under namespaces.
- Report types: lowercase, hyphen-separated, matching the directory name. Example: `debrief`.
- Worker names: lowercase, role-focused. Example: `investigator.md`.
- Script names: lowercase, hyphen-separated, descriptive. Example: `detect-env.py`.

Requirements:

- `name` is lowercase with hyphens and matches the directory name.
- `description` is under 1024 characters.
- The description states what the skill does and when to use it, with trigger keywords.
- Write the description in third person.
- `version` follows semantic meaning for schema or behavior changes.

The description is the only thing another agent sees when choosing whether to load the skill. Make it precise.

Good:

```
Reviews code for security issues in web applications. Use when asked to audit, secure, or harden code, or when the user mentions OWASP, injection, authentication, secrets, or vulnerabilities.
```

Bad:

```
Helps with code security.
```

---

## 6. Harness-agnostic and project-agnostic language

### 6.1 Harness-agnostic

Skills must not assume a specific agent harness, tool name, slash command, or vendor API.

| Bad | Good |
|-----|------|
| Run `/debrief OC-1234`. | Invoke the debrief skill for ticket OC-1234. |
| Call the `Agent` tool. | Spawn a focused worker. |
| Use `git status`. | Check the current working state. |

If a harness-specific detail is unavoidable, isolate it in a clearly labeled reference file.

### 6.2 Project-agnostic

A skill must not hardcode project-specific tools, paths, APIs, or conventions.

| Bad | Good |
|-----|------|
| Open Jira ticket PROJ-123. | Open the configured issue tracker for ticket PROJ-123. |
| Run `npm test`. | Run the project's test command. |
| Read `src/app/config.ts`. | Read the project's configuration entry point. |

The skill should detect the environment, consult config, or ask the user.

---

## 7. Global skills vs project-specific skills

### 7.1 Global skills

A global skill is installed once and used across any project, user, harness, and model.

Global skills must be:

- Fully harness-agnostic.
- Fully project-agnostic.
- Self-configuring through detection and config.
- Clear about dependencies, required capabilities, and external tools.

Any assumption, dependency, or required capability must be documented explicitly.

### 7.2 Project-specific skills

A project-specific skill lives inside a single project and can relax some portability constraints.

However, it should still:

- Follow the same structural and compositional guidelines.
- Remain as harness-agnostic and model-agnostic as possible.
- Declare dependencies and assumptions.
- Be written as a reusable pattern, even if it starts project-specific.

### 7.3 Declaring dependencies

A skill must declare:

- Other skills it expects to be available.
- External tools, APIs, MCP servers, or extensions it requires.
- Specific scripts, files, or conventions it relies on.
- Environment variables or secure stores it references.

Dependencies are not inherently bad. Hidden dependencies are.

---

## 8. Configuration and self-improvement

### 8.1 Config location

Configuration lives at the project level:

```
{project-root}/.agents/config/
├── shared.yaml              # cross-skill settings
└── {skill-name}.yaml        # skill-specific config + notes
```

User-level skills write project-level config.

Shared config is loaded first. Skill-specific config overrides shared values. The skill documents which shared keys it reads.

### 8.2 Config + notes structure

```yaml
preferences:
  issue_tracker: jira
  output_format: md

notes:
  - text: "Jira Cloud API requires email + token; use JIRA_EMAIL and JIRA_TOKEN env vars."
    category: gotcha
```

- `preferences` are machine-readable settings.
- `notes` are human-readable operational memory.

### 8.3 Bootstrap routine

A configurable skill follows a load-detect-validate-resolve-persist-execute-curate routine.

- Load existing shared config and skill-specific config.
- Detect the environment.
- Validate whether config matches the environment and is sufficient.
- Resolve ambiguity by asking the user.
- Persist choices and reasoning.
- Execute using resolved config.
- Curate notes afterward.

See the config file example in [Appendix A](#appendix-a-example-files) for a concrete example of a configured skill.

### 8.4 Notes are memory, not logs

Only record information that changes how a future invocation behaves. If the information is only useful for the current session, do not add it.

Note categories:

| Category | Purpose |
|----------|---------|
| `workaround` | A non-obvious method that worked. |
| `preference` | User's stated preference. |
| `assumption` | Something taken as true that could change. |
| `gotcha` | A trap the skill hit. |
| `decision` | A deliberate choice with rationale. |

Never overwrite existing config without asking.

---

## 9. Shared context and reports

### 9.1 Context directory

Skills share context by reading and writing reports in a well-known location:

```
{project-root}/.agents/context/{report-type}/{key}.md
```

Organize by report type, not by producing skill.

### 9.2 Report schema

Reports use frontmatter and markdown body:

```yaml
---
skill: debrief
version: 1
ticket: OC-1234
generated_at: 2026-06-26T08:42:00Z
summary: "One-sentence synthesis."
artifacts:
  - .agents/context/baseline/OC-1234-initial.md
---
```

A skill must document:

- What reports it produces.
- What reports from other skills it consumes.
- The schema and freshness expectations.

### 9.3 Cross-skill consumption

Do not fail silently if a consumed report is missing. If a fallback path has been approved and recorded in config notes, you may use it. Otherwise, note the gap or consult the user.

Treat reports as potentially stale. Check timestamps and underlying changes before relying on them.

---

## 10. Subagent delegation

### 10.1 When to delegate

Delegate when:

- The sub-task is large enough to dilute the main skill's context.
- The sub-task has a different focus than the main skill.
- The sub-task can return a clean artifact or finding.
- The main skill should remain a conductor or reviewer.

Do not delegate when:

- The task is small and sequential.
- The cost of context handoff exceeds the benefit.
- The sub-task requires ongoing user collaboration that the main skill should own.

### 10.2 Worker personas

Define workers in `subagents/`. Each prompt must state:

- Role and scope.
- What it should do.
- What tools or capabilities it may use.
- What it must not do.
- What format to return.

Keep worker prompts focused. A worker does not need the full skill philosophy. It needs:

- The specific task.
- The boundaries.
- The tools it may use.
- The return format.

A worker should reference shared context rather than duplicate it.

### 10.3 Standard return contract

Workers return structured results:

```yaml
---
status: complete | partial | needs_input | blocked
artifacts:
  - path/to/artifact.md
---

## Summary
...

## Findings
- ...

## Decisions made
- ...

## Open questions
- ...

## Blockers
- ...
```

The return contract should be defined once, in the skill's `references/SUBAGENTS.md` or a shared contract file, and referenced by each worker prompt rather than duplicated.

A worker must not ask the user directly unless explicitly authorized. It returns `needs_input`, and the main skill owns the user interaction.

---

## 11. State management

### 11.1 Stateless skills

Guideline skills are stateless. Running twice produces the same behavior.

### 11.2 Stateful skills

Workflow and conductor skills maintain state.

A stateful skill must document:

- Where state lives.
- The state schema.
- How to resume from existing state.
- How it avoids duplicating state on re-run.

### 11.3 State lifecycle

Treat state as living documents:

- Drafts.
- Reports.
- Refined reports.
- Checkpoints.

Append important decisions rather than silently overwriting them. Define a pruning or archiving strategy so state files do not grow indefinitely.

---

## 12. Explicitness, failure, and user consultation

A skill must be explicit about failure, ambiguity, and assumptions. It must not silently skip over problems or proceed on guesses.

### 12.1 Decision thresholds

| Situation | Behavior |
|-----------|----------|
| Context is clear and tools are available. | Proceed autonomously. |
| A minor convenience is missing but an equivalent path exists and was previously approved. | Use the approved fallback. |
| Something is missing, ambiguous, failed, or contradicts assumptions. | Pause and consult the user. |

An approved fallback is a previous user decision or preference recorded in config notes. If no note exists, the skill must consult the user before using a fallback for the first time.

### 12.2 How to consult

When pausing, explain:

- What is missing or unclear.
- Why it matters.
- What options the skill considered.
- What the skill recommends, if anything.

Bad:

> I need input.

Good:

> I detect branches `main` and `develop` but no stored default branch. Which should I use, or should I store `main` as the default?

### 12.3 Never proceed on significant assumptions

If proceeding would require a guess about user intent, stop and ask. The skill should be decisive but honest.

---

## 13. Security

- Never store secrets in skill files or config files.
- Reference environment variables or secure stores.
- Be explicit about required tools, APIs, and external services.
- Document what data leaves the local machine.
- Destructive actions require explicit user confirmation.
- Prefer read-only operations during investigation.
- Fail closed if a required capability is missing.

A skill should be safe to use in an untrusted project by default.

---

## 14. Validation and testing

Validate a skill through structure checks and behavioral scenarios.

Structure checks:

- Frontmatter is complete and correct.
- Reference links resolve.
- Language is harness-agnostic and project-agnostic.
- Progressive disclosure is followed.

Behavioral scenarios:

- Happy path.
- Missing config.
- Missing context report.
- Worker returns `blocked`.
- Worker returns `needs_input`.
- User rejects a proposal.
- Stale context report.

A checklist catches structure. Scenarios catch behavior.

---

## 15. Context-window discipline

Skills should stay small enough that the agent can load them without losing surrounding context.

- Keep `SKILL.md` under 300 lines where possible.
- Keep examples in `SKILL.md` minimal; expand them in `references/EXAMPLES.md`.
- If a skill covers multiple decision domains, split it.
- A subagent should receive only the context it needs for its task.
- A worker prompt should be shorter than the parent skill, not a copy of it.

If `SKILL.md` grows, move detail outward before it becomes a manual.

---

## 16. Skill dependencies and composition

A skill should declare what it needs from other skills. The canonical place is `references/DEPENDENCIES.md`. For simple cases, you may also use these proposed frontmatter fields:

```yaml
---
name: my-skill
consumes:
  - .agents/context/debrief/{ticket}.md
requires:
  - baseline
  - debrief
---
```

Use `references/DEPENDENCIES.md` if the dependency graph is complex.

A consuming skill must handle absence gracefully: either fall back to an approved alternative, note the gap, or consult the user.

---

## 17. Versioning and migration

When a skill's output schema, config schema, or behavior changes significantly, bump the version.

A skill should document:

- What changed.
- Whether older context reports remain compatible.
- How to migrate or mark stale reports.

Context reports should include the producing skill's version so consumers can handle older formats.

---

## Final principles

- A skill is a small philosophy for one domain, expressed through guidelines, delegation, shared context, and self-improving config.


- Delegate by default. Compose with other skills.
- Build modular, reusable pieces.
- Be global-first in portability.
- Be explicit about failure and assumptions.
- Consult the user rather than guess.
- Keep `SKILL.md` lean. Put detail where it belongs.
- The skill guides. The agent decides.

---

## Appendix A: Example files

### Example `SKILL.md`

```markdown
---
name: debrief
description: Understand a ticket or task and build confidence in it. Use when asked to investigate, understand, or summarize a ticket, task, or issue.
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "1.0"
---

# Debrief

## Purpose

Build a complete, validated understanding of a ticket or task so the agent can explain it, answer questions, and identify likely changes.

## When to use

- A user asks about a ticket.
- A user wants to understand a task.
- Another skill needs ticket context.

## Core workflow

- Identify the ticket source from config or detection.
- Gather ticket details.
- Explore the codebase and docs relevant to the ticket.
- Build confidence incrementally.
- Produce a debrief report in `.agents/context/debrief/{ticket}.md`.

## Out of scope

- This skill does not implement fixes.
- It does not make irreversible decisions.

## References

- [Config pattern](references/CONFIG_PATTERN.md)
- [Context reports](references/CONTEXT_REPORTS.md)
- [Subagent delegation](references/SUBAGENTS.md)
```

### Example `README.md`

```markdown
# debrief

Investigates tickets and produces structured reports that other skills can consume.

## Purpose

Build a complete, validated understanding of a ticket or task.

## When to use

Use this skill when:

- A user asks about a ticket.
- A user wants to understand a task.
- Another skill needs ticket context.

## Directory layout

```
debrief/
├── SKILL.md
├── README.md
├── references/
│   ├── CONFIG_PATTERN.md
│   ├── CONTEXT_REPORTS.md
│   └── SUBAGENTS.md
└── scripts/
    └── detect-env.py
```

## Key conventions

- Produces reports in `.agents/context/debrief/{ticket}.md`.
- Detects the issue tracker from the project environment.
- May delegate focused investigation to subagents.
```

### Example config file

```yaml
# .agents/config/debrief.yaml

preferences:
  issue_tracker: jira
  project_key: PROJ
  output_format: md

notes:
  - text: "Jira Cloud API requires email + token; use JIRA_EMAIL and JIRA_TOKEN env vars."
    category: gotcha
    added: "2026-06-26"
```

### Example context report

```markdown
---
skill: debrief
version: 1
ticket: OC-1234
generated_at: 2026-06-26T08:42:00Z
summary: "Auth guard race condition during token refresh."
artifacts:
  - .agents/context/baseline/OC-1234-initial.md
---

# Debrief: OC-1234

## Understanding
...

## Key findings
- ...

## Open questions
- ...

## Files likely to change
- ...
```

### Example worker prompt

```markdown
# Investigator

You are an investigator worker for the `debrief` skill.

Your job: explore the codebase and identify files and decisions relevant to a ticket.

In scope:
- Read source files, tests, ADRs, and docs.
- Identify files likely to change.
- Note architectural constraints.

Out of scope:
- Do not propose fixes.
- Do not write code.
- Do not ask the user questions.

Return format: use the standard worker return contract.
```

### Script conventions

Scripts used by skills should be:

- **Deterministic.** Given the same input and environment, they produce the same result. They should not rely on randomness or undocumented side effects.
- **Documented.** Include a docstring or header explaining what the script does, what it expects, and what it returns.
- **Safe.** Do not perform destructive operations unless explicitly designed and labeled to do so. Prefer read-only inspection.
- **Isolated.** They should not ask the user for input. If input is needed, the skill should collect it and pass it as arguments or environment variables.
- **Failure-explicit.** Exit with a non-zero status and a clear message on failure.

```python
#!/usr/bin/env python3
"""Detect available issue trackers in the current project."""
import os


def detect_issue_tracker():
    """Return the detected issue tracker or None."""
    if os.path.exists(".github/ISSUE_TEMPLATE"):
        return "github"
    if os.path.exists("jira.config"):
        return "jira"
    return None


if __name__ == "__main__":
    print(detect_issue_tracker())
```

### Example `references/CONFIG_PATTERN.md` excerpt

```markdown
## Config keys

| Key | Required | Description |
|-----|----------|-------------|
| `issue_tracker` | yes | Tool used for tickets: `jira`, `github`, `linear`, etc. |
| `project_key` | no | Project key for ticket lookups. |
| `output_format` | no | Report format: `md` or `html`. Default: `md`. |

## Environment variables

- `JIRA_EMAIL` and `JIRA_TOKEN` for Jira Cloud authentication.
- `GITHUB_TOKEN` for private GitHub repositories.
```

### Example `references/DEPENDENCIES.md`

```markdown
# Dependencies

## Required skills

- `baseline` — for capturing initial UI or system state.

## Consumed reports

- `.agents/context/baseline/{key}.md`

## Required tools

- Access to the project's issue tracker.
- Ability to read source files and documentation.
```
