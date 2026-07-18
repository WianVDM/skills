# Subagent Delegation

`plan-next` delegates focused tasks to workers. The main skill remains the conductor.

## Standard worker return format

Workers should return structured markdown:

```markdown
---
status: complete
---

## Summary
Brief summary of what was done.

## Findings
Structured findings.

## Recommended Next Action
What the main agent should do next.
```

Status values: `complete`, `in-progress`, `blocked`.

## Subagents

| Subagent | Responsibility |
|----------|----------------|
| `context-auditor` | Summarize context and assess readiness. |
| `skill-discovery-agent` | Discover available skills and read frontmatter. |
| `skill-profiler` | Build capability profiles from skill references. |
| `skill-evaluator` | Score each skill against the context. |
| `plan-builder` | Group selected skills into phases with dependencies. |

State, revisions, and finalization tracking are delegated to the `checkpoint` block; no private worker is needed.

Workers do not write directly to plan files unless explicitly instructed. They return findings for the main agent to integrate.
