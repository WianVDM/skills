# Context-file pattern

A **context file** is always-on guidance that lives in the project context, not a skill. It is loaded once at the start of a session and remains in the agent's context throughout. It is not invoked on demand like a skill.

Context files and skills are complementary. Context files set the baseline; skills provide reusable, on-demand workflows.

---

## When to use a context file

Use a context file when:

- The guidance applies to almost every task in the project.
- The guidance is stable and not tied to a specific workflow.
- The goal is to shape the agent's baseline behavior, not to trigger a reusable process.

Examples:

- `AGENTS.md` or `CONVENTIONS.md` — team conventions, coding standards, vocabulary.
- `.cursorrules` or `.claude/rules` — file-type or situation-specific rules.
- `CLAUDE.md` — project-specific instructions for a harness.

Do not use a context file when:

- The guidance is only relevant for specific tasks.
- The guidance is a reusable workflow with a clear trigger.
- Keeping the guidance always-on would waste context budget.

---

## Context file vs. skill

| Context file | Skill |
|--------------|-------|
| Always-on. | On-demand. |
| Loaded at session start. | Loaded when the description matches the task. |
| Sets baseline conventions. | Runs a specific workflow or provides specific reference. |
| Examples: `AGENTS.md`, `.cursorrules`, `.claude/rules`. | Examples: `review-ui`, `ticket-research`, `debrief`. |

A context file says "here is how we work here." A skill says "here is how to do this specific kind of work."

---

## When a skill becomes a context file

If a skill is always needed and has no clear trigger, it may be better as a context file. For example, a coding-conventions skill that fires on every code request is probably better as a context file or scoped rule.

Conversely, if a context file grows into a workflow with phases and outputs, it may be better as a skill.

---

## Boundary with rules

Some harnesses support **scoped rules** — guidance that applies to specific file types or situations. These are also context files, just with narrower scope. A skill is not a rule and a rule is not a skill, though they can reinforce each other.

When a skill and a context file give conflicting guidance, the model receives both and resolves the conflict heuristically; the exact precedence is harness-dependent. There is no documented universal precedence rule across harnesses. The best practice is to avoid overlap: let context files set baseline conventions and let skills handle specific workflows.

---

## Example: project conventions context file

A context file is **not** a skill, so it does not have a `SKILL.md`. Instead, it lives at the project root and is loaded once per session. Below is a full `CONVENTIONS.md` for a TypeScript / React project.

### `CONVENTIONS.md`

```markdown
# Project conventions

This project uses TypeScript, React, and Vitest.

## Code style

- Prefer functional components with hooks.
- Keep components under ~100 lines; extract at natural seams.
- Use `const` assertions for literal types.
- Avoid `any`; prefer `unknown` with runtime checks.

## Testing

- Write tests through the public component interface.
- One test per public behavior.
- Use factory functions for test data, not shared mutable fixtures.

## Dependencies

- Use the shared design-system components.
- Prefer `date-fns` for date manipulation.

## Out of scope for this file

- This file does not contain specific workflows. Use a skill for that.
- This file does not enforce discipline. Use a discipline skill for that.
```

### Why it works

- It is **always-on** but **short**: it sets the baseline without crowding every skill.
- It distinguishes **conventions** (this file) from **workflows** (skills) and **discipline** (skills).
- It avoids duplication: skills point to it for shared conventions rather than restating them.

---

## Research basis

- The **context stack** (always-on context, scoped rules, skills, hooks, MCP, subagents) is drawn from the research across Claude Code, Cursor, Codex, Aider, and Hermes. See [manifestos/architecture.md](../../manifestos/architecture.md) for the full stack.
- The **context-file pattern** as a distinct layer from skills is supported by the research on rules, context files, and skills boundaries.
- **Claude Code** explicitly distinguishes skills from `CLAUDE.md` and `.claude/rules`. **Cursor** provides `.cursorrules` and dynamic rules, with a `/migrate-to-skills` command that only migrates dynamic rules, not always-on rules. **Codex** uses `AGENTS.md` as a project-level context file.
- The observation that **always-on behavior is lost** when a rule is migrated to a skill is drawn from the Cursor migration research.
- The boundary between context files and skills is our own design choice, synthesized from the research: context files set the baseline; skills are on-demand, reusable workflows.

---

## Related documents

- [`../fundamentals/core/types/`](../fundamentals/core/types/) — choosing the right skill type.
- [`manifestos/architecture.md`](../../manifestos/architecture.md) — the full context stack.
