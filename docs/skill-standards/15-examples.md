# 15 — Examples

These examples show how the standards apply to real skill shapes. They are illustrative, not exhaustive. Use them as reference points when designing or reviewing a skill.

---

## Example 1 — Standalone / Atomic skill: `interview`

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

## Example 3 — Hybrid skill: `ticket-research`

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

- [Config pattern](references/CONFIG_PATTERN.md)
- [Context reports](references/CONTEXT_REPORTS.md)
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
- **Hybrid:** has a clear workflow plus embedded principles about confidence and scope.
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

A focused worker for a conductor or hybrid skill.

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
