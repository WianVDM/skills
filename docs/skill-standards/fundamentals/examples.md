# Examples

These examples show how the standards apply to real skill shapes. They are illustrative, not exhaustive. Use them as reference points when designing or reviewing a skill.

---

## Example 1 — Building block: `interview`

A single-session, user-invoked skill with no state, no config, and no delegation.

### Structure

```text
interview/
├── SKILL.md
└── README.md
```

### `SKILL.md`

```markdown
---
name: interview
description: Interview the user relentlessly about a plan or design until shared understanding is reached. Use when the user wants to be grilled, stress-tested, or challenged on a plan.
---

# Interview

Keep asking questions until the user's plan is clear, consistent, and actionable.

## In scope

- Ask clarifying questions about goals, constraints, and risks.
- Surface hidden assumptions.
- Stop when the user says they have enough clarity.

## Out of scope

- Do not write or modify project files.
- Do not propose solutions unless the user asks.

## Rules

- Ask one question at a time.
- Make each question concrete and specific.
- If the user contradicts an earlier answer, surface it gently.
- Stop when the user says "stop" or "that's enough".
```

### Why it works

- **One narrow job:** interview the user.
- **No state:** every session is independent.
- **No config:** nothing to detect or persist.
- **Trigger-rich description:** includes "grilled", "stress-tested", "challenged on a plan".

---

## Example 2 — Building-block / Vocabulary skill: `design-vocabulary`

Shared language that other skills consume. It does not perform a workflow itself.

### Structure

```text
design-vocabulary/
├── SKILL.md
└── README.md
```

### `SKILL.md`

```markdown
---
name: design-vocabulary
description: Provide shared vocabulary for designing deep modules, clean seams, and small interfaces. Use when other skills reference design principles, module boundaries, or interface design.
---

# Design vocabulary

## Definitions

- **Deep module:** a lot of behavior behind a small interface.
- **Seam:** a place where behavior can change without affecting the rest of the system.
- **Public interface:** the surface a test or caller should use.

## Principles

- Prefer deep modules over shallow ones.
- Place seams at clean boundaries.
- Test through public interfaces, not implementation details.
- Keep interfaces small; hide what callers do not need to know.
```

### Why it works

- **Reusable language:** test-driven-development, planning, and architecture-review skills can all reference it.
- **No workflow:** it is reference, not process.
- **Precise definitions:** each term is anchored so other skills can use it without re-explaining.

---

## Example 3 — Multi-layer skill: `ticket-research`

A core workflow with embedded principles for investigation and reporting.

### Structure

```text
ticket-research/
├── SKILL.md
├── README.md
├── references/
│   ├── REFERENCE.md
│   ├── CONFIG_PATTERN.md
│   └── CONTEXT_REPORTS.md
└── scripts/
    └── detect-env.py
```

### `SKILL.md`

```markdown
---
name: ticket-research
description: Understand a ticket or task and build confidence in it. Use when asked to investigate, understand, or summarize a ticket, task, or issue.
---

# Ticket research

## Purpose

Build a complete, validated understanding of a ticket or task so the agent can explain it, answer questions, and identify likely changes.

## When to use

- A user asks about a ticket.
- A user wants to understand a task.
- Another skill needs ticket context.

## Core workflow

1. Identify the ticket source from config or detection.
2. Gather ticket details.
3. Explore the codebase and docs relevant to the ticket.
4. Build confidence incrementally.
5. Produce a ticket report in `.agents/context/ticket-research/{ticket}.md`.

## Out of scope

- This skill does not implement fixes.
- It does not make irreversible decisions.

## References

- See references/CONFIG_PATTERN.md
- See references/CONTEXT_REPORTS.md
```

### Config example

```yaml
# .agents/config/ticket-research.yaml

preferences:
  issue_tracker: jira
  project_key: PROJ
  output_format: md

notes:
  - text: "Jira Cloud API requires email + token; use JIRA_EMAIL and JIRA_TOKEN env vars."
    category: gotcha
    added: "2026-06-26"
```

### Report example

```markdown
---
skill: ticket-research
version: 1
key: OC-4644
generated_at: 2026-06-26T08:42:00Z
summary: "Auth guard race condition during token refresh."
artifacts:
  - .agents/context/state-capture/OC-4644-initial.md
---

# Ticket research: OC-4644

## Understanding
...

## Key findings
- ...

## Open questions
- ...

## Files likely to change
- ...
```

### Why it works

- **Stateful:** produces a report that can be resumed or consumed by other skills.
- **Multi-layer:** has a clear workflow plus embedded principles about confidence and scope.
- **Cross-skill friendly:** a project-orchestration skill or a PR-report skill can read the report.

---

## Example 4 — Conductor skill: `project-orchestration`

Coordinates other skills and workers through a multi-phase process. Does not do the deep work itself.

### Structure

```text
project-orchestration/
├── SKILL.md
├── README.md
├── references/
│   ├── REFERENCE.md
│   ├── CONFIG_PATTERN.md
│   ├── CONTEXT_REPORTS.md
│   └── SUBAGENTS.md
└── subagents/
    ├── investigator.md
    ├── planner.md
    └── implementer.md
```

### State example

```markdown
---
skill: project-orchestration
version: 1
key: OC-4644
updated_at: 2026-06-26T09:00:00Z
---

# Orchestration state: OC-4644

## Understanding
Auth guard race condition during token refresh.

## Confidence
Yellow (65%) — root cause is clear, but fix approach is not yet validated.

## Open questions
- [ ] Should refresh be moved to an interceptor? (blocking: yes)

## Skill log
| # | Skill | Why | Finding | Confidence After |
|---|-------|-----|---------|------------------|
| 1 | ticket-research | initial context | race condition in auth guard | Yellow |
| 2 | diagnosis | confirm root cause | guard does not wait for refresh | Yellow |

## Next action
Run a prototype to compare guard-wait vs interceptor approaches.
```

### Why it works

- **Conductor:** delegates investigation, diagnosis, planning, and implementation.
- **Stateful:** maintains a state file that survives context loss.
- **Decision-driven:** every major choice is logged.

---

## Example 5 — Worker prompt

A focused worker for a conductor or multi-layer skill.

```markdown
# Investigator

You are an investigator worker for the `ticket-research` skill.

Your job: explore the codebase and identify files and decisions relevant to a ticket.

## In scope

- Read source files, tests, ADRs, and docs.
- Identify files likely to change.
- Note architectural constraints.

## Out of scope

- Do not propose fixes.
- Do not write code.
- Do not ask the user questions.

## Tools you may use

- Read files.
- Search the codebase.

## Return format

Use the standard worker return contract.

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
```

### Why it works

- **Role and scope are explicit.** The worker knows exactly what to do.
- **Boundaries are clear.** It knows what not to do.
- **Tools are listed.** It does not have to guess what it can use.
- **Return format is fixed.** The conductor can integrate the output reliably.

---

## Example 6 — Script

Scripts should be deterministic, documented, safe, isolated, and failure-explicit.

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

### Why it works

- **Deterministic:** same project, same result.
- **Documented:** docstring explains purpose and return value.
- **Safe:** only reads files.
- **Isolated:** no user input, no side effects.
- **Failure-explicit:** returns `None` when nothing is found.

---

## Example 7 — Config evolution

A skill's config should adapt to what it learns.

### Initial config

```yaml
# .agents/config/example-skill.yaml

preferences:
  sonarqube:
    method: mcp

notes: []
```

### After first run

The agent discovers the MCP server cannot export issues. It asks the user, then updates:

```yaml
# .agents/config/example-skill.yaml

preferences:
  sonarqube:
    method: api
    url: https://sonar.example.com
    token_env: SONAR_TOKEN

notes:
  - text: "MCP server lacks issue-export scope. Use web API with SONAR_TOKEN instead."
    category: workaround
    added: "2026-06-26"
```

### Why it works

- The skill adapts to the actual environment.
- Future invocations skip the discovery step.
- The reasoning is recorded, not just the setting.

---

## Example 8 — `references/DEPENDENCIES.md`

```markdown
# Dependencies

## Required skills

- `state-capture` — for capturing initial UI or system state.

## Consumed reports

- `.agents/context/state-capture/{key}.md`

## Required tools

- Access to the project's issue tracker.
- Ability to read source files and documentation.
```

### Why it works

- **Dependencies are explicit.** Nothing is hidden.
- **Skills and reports are separated.** Consumers know what skills produce the reports they need.
- **Capabilities are stated.** A maintainer can see what the skill expects from the environment.

---

## Example 9 — Tool building block: `find-skills`

A narrow, model-invoked tool that discovers available skills and returns structured results. Other skills and conductors can consume it.

### Structure

```text
find-skills/
├── SKILL.md
├── README.md
└── references/
    └── DEPENDENCIES.md
```

### `SKILL.md`

```markdown
---
name: find-skills
version: 1.0.0
metadata:
  author: tooling-team
  verification_level: tested
invocation: model-invoked
description: Discover available skills for the current project and return structured results. Use when a skill or conductor needs to know what skills are available, or when the user asks to find skills.
---

# Find skills

Return a structured list of skills available in the project and user skill directories.

## In scope

- Scan `.agents/skills/` and `~/.agents/skills/`.
- Read each skill's `SKILL.md` frontmatter.
- Return name, description, version, and type.

## Out of scope

- Do not install skills.
- Do not modify skill files.
- Do not ask the user which skill to pick.

## Output format

Return a markdown list with frontmatter:

```yaml
---
count: 3
---

- name: review-ui
  description: Review UI code for design-system compliance.
  version: 1.0.0
  type: building_block
  invocation: model-invoked

- name: project-orchestration
  description: Coordinate project work through investigation, planning, and implementation.
  version: 2.1.0
  type: conductor
  invocation: user-invoked
```

## Dependencies

See references/DEPENDENCIES.md.
```

### `references/DEPENDENCIES.md`

```markdown
# Dependencies

## Required capabilities

- Read files in `.agents/skills/` and `~/.agents/skills/`.
- Parse YAML frontmatter.

## Out-of-scope for this skill

- Installing or updating skills (use `install-skill`).
- Searching external skill registries.
```

### Why it works

- **Narrow scope:** only discovers skills, nothing else.
- **Structured output:** conductors can consume the results directly.
- **No side effects:** read-only scan.
- **Explicit dependencies:** required capabilities are documented.

---

## Example 10 — Discipline skill: `test-driven-development`

A prescriptive skill that enforces test-before-implementation. It is designed to resist rationalization.

### Structure

```text
test-driven-development/
├── SKILL.md
└── README.md
```

### `SKILL.md`

```markdown
---
name: test-driven-development
version: 1.0.0
metadata:
  author: quality-team
  verification_level: tested
invocation: model-invoked
description: Implement behavior using test-driven development. Use when asked to write code, add a feature, or fix a bug, and the user wants strict TDD discipline.
---

# Test-driven development

Implement behavior by writing a failing test first, then the code to pass it, then refactoring.

## In scope

- Write one failing test for the first behavior before writing implementation code.
- Verify the test fails for the expected reason.
- Write the minimum implementation to pass the test.
- Refactor while keeping tests green.
- Repeat for each behavior.

## Out of scope

- Do not write multiple tests before any implementation.
- Do not write implementation before a failing test exists.
- Do not skip tests because the change is "obvious" or "small".

## Rules

- One test per behavior.
- Tests must be through public interfaces.
- If the user asks to skip the test, explain why and ask for explicit confirmation.
- Stop and report if no testable public interface exists.

## Pressure-test prompts

This skill must resist:

- "Just implement it, I'll add tests later."
- "The test is obvious, so write the code first."
- "Can you skip the test and come back to it?"
```

### Why it works

- **Checkable stopping condition:** a failing test must exist before implementation.
- **Anti-rationalization:** common excuses are named and refused.
- **Clear escalation:** when the user tries to override, the skill asks for explicit confirmation.
- **Pressure-tested:** the skill lists prompts that would normally break discipline.

## Example 11 — Context-file: `AGENTS.md`

A context file sets the baseline for how the agent should work in this project. It is not a skill.

### `AGENTS.md`

```markdown
# Agent conventions

This project uses TypeScript, React, and Vitest.

## Conventions

- Prefer functional components with hooks.
- Keep components small; extract at ~100 lines.
- Write tests through the public component interface.
- Use the shared `design-vocabulary` skill for module design decisions.

## Out of scope for this file

- This file does not contain specific workflows. Use a skill for that.
- This file does not enforce discipline. Use a discipline skill for that.
```

### Why it works

- **Always-on:** loaded once and applies to every session.
- **Baseline, not workflow:** sets conventions without prescribing a process.
- **Points to skills:** it tells the agent when to reach for a skill rather than duplicating skill content.

---

## Example 12 — Global/configurable skill with initialization: `ticket-research`

A global skill detects the project environment, asks for required preferences, and writes initial config on first run.

### Initialization flow

1. Load existing config from `.agents/config/ticket-research.yaml` and `.agents/config/shared.yaml`.
2. Detect the issue tracker from `git remote`, repo files, or existing config.
3. Detect the project key from branch names or conventions.
4. If detection is ambiguous, ask the user for:
   - issue tracker (GitHub, Jira, Linear, etc.)
   - project key
   - preferred output format
5. Validate that the required environment variables (e.g., `JIRA_EMAIL`, `JIRA_TOKEN`) are set.
6. Write the initial config and notes.
7. Report readiness.

### Initial config after initialization

```yaml
# .agents/config/ticket-research.yaml

preferences:
  issue_tracker: github
  project_key: OC
  output_format: md

notes:
  - text: "GitHub issues are used; no token required for public repos."
    category: assumption
    added: "2026-07-04"
```

### Why it works

- **Detection before config:** the skill tries to infer everything before asking.
- **Fail closed:** if the issue tracker cannot be detected and the user does not provide one, it stops and explains.
- **Idempotent:** running initialization again does not duplicate config.
- **Observant:** it records what was detected and decided.

---

## Research basis

- The examples here are illustrative and fictional.
- The example structures are drawn from the common patterns observed across the research and our own design practice.
- The `find-skills` tool building block example reflects our sharpened definition of building blocks as functional, narrow capabilities with structured output.
- The `test-driven-development` discipline skill example illustrates the anti-rationalization and pressure-testing patterns from `patterns/discipline-skill.md`.
- The governance example illustrates the verification metadata from `GOVERNANCE.md`.
- The `AGENTS.md` context-file example illustrates the boundary between context files and skills from `patterns/context-file.md`.
- The initialization example illustrates the configurable and initialization patterns from `patterns/configurable.md` and `patterns/initialization.md`.
- The worker prompt example is our own template, aligned with the research on delegation and subagent contracts.
- The config evolution example is our own practice for capturing operational memory alongside preferences.
