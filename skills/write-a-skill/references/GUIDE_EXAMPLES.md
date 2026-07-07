# Example Skills

These examples show how the framework applies to guideline, workflow, and conductor skills. All names, paths, and tools are fictional.

---

## Example 1: guideline skill — `code-style`

### Purpose

Tell the agent how to write and review TypeScript code in this project.

### Structure

```
code-style/
├── SKILL.md
└── README.md
```

### SKILL.md

```markdown
---
name: code-style
description: Enforce TypeScript coding conventions for this project. Use when writing, reviewing, or refactoring TypeScript code.
---

# Code Style

## Principles

- Prefer small, single-responsibility functions.
- Use explicit names; avoid abbreviations.
- Prefer early returns over nested conditionals.
- Keep files under 400 lines.

## TypeScript specifics

- Use strict TypeScript settings.
- Avoid `any`; use `unknown` when type is uncertain.
- Prefer interfaces over type aliases for object shapes.
- Use `readonly` for immutable arrays and properties.

## Testing

- Co-locate tests next to source files.
- Use descriptive test names that explain behavior, not implementation.
```

### Why it works

- Stateless: no config, no context, no delegation.
- Focused: only coding style, not general development.
- Trigger-rich description: "writing, reviewing, refactoring TypeScript code."

---

## Example 2: workflow skill — `ticket-brief`

### Purpose

Investigate a ticket and produce a structured report that other skills can consume.

### Structure

```
ticket-brief/
├── SKILL.md
├── README.md
├── references/
│   ├── REFERENCE.md
│   └── CONFIG_PATTERN.md
└── scripts/
    └── detect-env.py
```

### Config example

```yaml
# {config}/ticket-brief.yaml

preferences:
  issue_tracker: generic
  project_key: PROJ
  baseline_tool: generic-ui-test
  output_format: md

notes:
  - text: "Generic Cloud API requires email + token; use ISSUE_EMAIL and ISSUE_TOKEN env vars."
    category: gotcha
  - text: "User prefers briefs focused on files to change, not full system context."
    category: preference
```

### Report example

```markdown
---
skill: ticket-brief
version: 1.0.0
ticket: PROJ-1234
generated_at: 2026-06-26T08:42:00Z
summary: "Auth guard race condition when token refresh overlaps with route navigation"
artifacts:
  - {context}/baseline/PROJ-1234-initial.md
---

# Ticket brief: PROJ-1234

## Understanding
...

## Files likely to change
- `src/app/guards/auth.guard.ts`
- `src/app/services/auth.service.ts`

## Open questions
- [ ] Should refresh happen in an interceptor or in the guard?

## References
- `docs/adr/0003-auth-flow.md`
```

### Why it works

- Stateful: produces a report that can be resumed or consumed by other skills.
- Configurable: adapts to the project's issue tracker and baseline tools.
- Cross-skill friendly: `ship-feature` and `release-report` can read the report.

---

## Example 3: conductor skill — `ship-feature`

### Purpose

Coordinate multiple skills to move from ticket understanding to implementation.

### Structure

```
ship-feature/
├── SKILL.md
├── README.md
├── references/
│   ├── REFERENCE.md
│   ├── CONFIG_PATTERN.md
│   ├── CONTEXT_REPORTS.md
│   ├── WORKER_CONTRACT.md
└── subagents/
    ├── investigator.md
    ├── planner.md
    └── implementer.md
```

### State example

```markdown
---
skill: ship-feature
version: 1.0.0
ticket: PROJ-1234
updated_at: 2026-06-26T09:00:00Z
---

# Ship-feature state: PROJ-1234

## Understanding
Auth guard race condition during token refresh.

## Confidence
Yellow (65%) — root cause is clear, but fix approach is not yet validated.

## Open questions
- [ ] Should refresh be moved to an interceptor? (blocking: yes)

## Skill log
| # | Skill | Why | Finding | Confidence After |
|---|-------|-----|---------|------------------|
| 1 | ticket-brief | initial context | race condition in auth guard | Yellow |
| 2 | example-debugger | confirm root cause | guard does not wait for refresh | Yellow |

## Next action
Run `example-ideator` to compare guard-wait vs interceptor approaches.
```

### Why it works

- Conductor: delegates investigation, diagnosis, planning, and implementation to focused workers.
- Stateful: maintains a state file that survives context loss.
- Decision-driven: every major choice is logged.

---

## Example 4: config + notes evolution

### Initial config

```yaml
preferences:
  quality_gate:
    method: mcp

notes: []
```

### After first run

The agent discovers the MCP server cannot export issues. It asks the user, then updates:

```yaml
preferences:
  quality_gate:
    method: api
    url: https://quality.example.com
    token_env: QUALITY_TOKEN

notes:
  - text: "MCP server lacks issue-export scope. Use web API with QUALITY_TOKEN instead."
    category: workaround
    added: "2026-06-26"
```

### Why it works

- The skill adapts to the actual environment.
- Future invocations skip the discovery step.
- The reasoning is recorded, not just the setting.
