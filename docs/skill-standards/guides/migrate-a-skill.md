# Migration Guide

Skills change shape as they mature: a local helper becomes a global reusable block, a context file grows into a workflow, or the standard itself moves to a new version. This guide provides safe paths for the most common migrations.

## Quick guide

1. See the sections below for the common shape changes.
2. Update the `version` metadata if the contract or schema changed and the skill is shared or consumed. See [`reference/governance.md`](../reference/governance.md) for governance rules.
3. Re-run trigger and behavioral evals after the migration. See [`reference/trigger-evals.md`](../reference/trigger-evals.md) and [`reference/evaluation-framework.md`](../reference/evaluation-framework.md).

A good migration preserves the **core contract** while changing how the skill is discovered, invoked, or packaged. Do not migrate for its own sake; migrate when the new shape solves a real problem.

---

## Project-specific skill → global / pluggable skill

A project-specific skill works in one repo because it hardcodes paths, conventions, or config. To make it global:

### 1. Replace hardcoded project details with detection or config

| Project-specific | Global |
|------------------|--------|
| `src/components` | Detect the source directory from the project layout. |
| `npm test` | Detect the test command from lockfiles or config. |
| `JIRA_PROJECT=PROJ` | Read from `requirements.environment_variables` or ask the user. |
| `.github/ISSUE_TEMPLATE` | Use a script to detect the issue tracker. |

Push detected values into `.agents/config/{skill-name}.yaml` and persist notes about what was discovered.

### 2. Declare dependencies in `skills.json`

A global skill must declare what it needs so consumers can validate it before loading:

```json
{
  "name": "ticket-research",
  "version": "1.0.0",
  "skills": ["ticket-research"],
  "requirements": {
    "tools": ["read_file", "search_code"],
    "binaries": ["jq"],
    "environment_variables": ["ISSUE_TRACKER_API_TOKEN"]
  }
}
```

### 3. Add an initialization phase

Global skills often need first-run setup. Use the load-detect-validate-resolve-persist-execute-curate routine from `patterns/configurable.md` and `patterns/initialization.md`.

### 4. Fail closed on missing environment

If the skill cannot detect its environment and the user does not provide config, stop and explain what is missing. Do not guess.

### Example: `SKILL.md` before and after

**Before — project-specific**

```markdown
---
name: ticket-research
version: 1.0.0
invocation: model-invoked
description: Understand a ticket in Jira project PROJ.
---

# Ticket research

1. Call the Jira API for project PROJ.
2. Read `src/` to find relevant files.
3. Write a report to `.agents/context/ticket-research/{key}.md`.
```

**After — global**

```markdown
---
name: ticket-research
version: 1.0.0
invocation: model-invoked
description: Understand a ticket or task and build confidence in it. Use when asked to investigate, understand, or summarize a ticket, task, or issue.
---

# Ticket research

1. Load config from `.agents/config/ticket-research.yaml`.
2. Detect the issue tracker from the project or config.
3. Fetch the ticket details.
4. Explore the codebase for relevant files.
5. Write a report to `.agents/context/ticket-research/{key}.md`.

## Out of scope

- Do not make changes to the codebase unless asked.
- Do not guess the issue tracker; stop and ask if it cannot be detected.
```

---

## Rule / context-file → skill

A context file or rule becomes a skill when it grows a clear trigger, a specific workflow, and an output.

### 1. Identify when the guidance should fire

A context file is always-on. A skill is on-demand. Ask: *what user prompt should load this skill?* If there is no clear trigger, it should probably stay a context file.

### 2. Extract the workflow and contract

Move from broad conventions to a narrow process:

- **Context file:** "Write tests through public interfaces."
- **Skill:** "Write one failing test for the public behavior before any implementation code."

### 3. Add frontmatter and a description

Give the skill identity, a routing description, and an invocation mode.

```yaml
---
name: test-driven-development
version: 1.0.0
invocation: model-invoked
description: Implement behavior using test-driven development. Use when asked to write code, add a feature, or fix a bug, and the user wants strict TDD discipline.
---
```

### 4. Leave the baseline in the context file

Do not delete the original context file. Keep it as a lightweight baseline. The skill should reference it for shared conventions, not duplicate them.

### 5. Add evaluation

Because the skill is now triggered, write trigger evals to confirm it fires at the right times. See [reference/trigger-evals.md](../reference/trigger-evals.md) and [reference/evaluation-framework.md](../reference/evaluation-framework.md).

### Example: from `CONVENTIONS.md` to `tdd-discipline/SKILL.md`

**`CONVENTIONS.md` (baseline)**

```markdown
# Conventions

- Write tests through public interfaces.
- Keep tests focused on one behavior.
```

**`tdd-discipline/SKILL.md` (skill)**

```markdown
---
name: test-driven-development
version: 1.0.0
invocation: model-invoked
description: Implement behavior using test-driven development. Use when asked to write code, add a feature, or fix a bug, and the user wants strict TDD discipline.
---

# Test-driven development

## In scope

- Write one failing test for the public behavior before writing implementation code.
- Verify the test fails for the expected reason.
- Write the minimum implementation to pass the test.
- Refactor while keeping tests green.

## Out of scope

- Do not write multiple tests before any implementation.
- Do not skip tests because the change is "obvious" or "small".

## Rules

- If the user asks to skip the test, explain why and ask for explicit confirmation.
- Stop and report if no testable public interface exists.
```

---

## Skill → context-file

The reverse migration is also valid. A skill should become a context file when:

- It is needed on almost every turn.
- It has no clear trigger or workflow.
- The user would otherwise have to invoke it by hand every session.

### Steps

1. Move the stable conventions into `AGENTS.md`, `CONVENTIONS.md`, or a scoped rule.
2. Remove the `SKILL.md` or mark it as deprecated.
3. Delete any model-invoked routing description; the guidance is now always-on.
4. Keep any workflow that has a clear trigger as a separate skill.

### Warning

Do not migrate a skill to a context file just because it is small. A small, narrowly triggered skill is still a skill. A context file is for always-on baselines.

---

## Standard v1 → v2

This standard is versioned. When the format or package schema changes, skills may need to be updated to remain compliant.

### General steps

1. Read the v2 changelog and schema differences.
2. Update all `SKILL.md` frontmatter to match the new schema.
3. Update all `skills.json` manifests to match the new package schema.
4. Re-run the `evals/evals.json` suite.
5. Bump the skill version if the schema change affects consumers.
6. Document the migration path in `references/VERSIONING.md`.

### Common v1 → v2 changes to watch for

| v1 pattern | v2 pattern | Action |
|------------|------------|--------|
| `version` inside `metadata` | `version` top-level | Move `version` out of `metadata`. |
| `requires` / `consumes` in frontmatter | `requirements` in `skills.json` | Use the package-level dependency model. |
| Harness hints as core fields | harness hints separated | Move `allowed-tools` and similar to harness hints. |

### Fallback strategy

If a harness does not yet support the v2 schema, maintain a v1-compatible copy and a v2 copy. The plain-markdown export path from [`patterns/portability.md`](../patterns/portability.md) can help bridge the gap.

---

## Migration checklist

- [ ] The new shape solves a real problem, not a cosmetic one.
- [ ] The core contract (what the skill does and when) is preserved.
- [ ] Hardcoded project details are replaced by detection, config, or explicit user input.
- [ ] Dependencies are declared in `skills.json` or `references/DEPENDENCIES.md`.
- [ ] The skill is still portable and harness-agnostic where required.
- [ ] Trigger evals are updated if the invocation model changed.
- [ ] The version is bumped if consumers are affected.
- [ ] The original artifact (context file, old skill directory) is deprecated, not silently deleted.

---

## Related documents

- [`patterns/global-pluggable.md`](../patterns/global-pluggable.md) — making a skill work in any project.
- [`patterns/configurable.md`](../patterns/configurable.md) — config and notes.
- [`patterns/initialization.md`](../patterns/initialization.md) — first-run setup.
- [`patterns/context-file.md`](../patterns/context-file.md) — when to use a context file instead of a skill.
- [`patterns/discipline-skill.md`](../patterns/discipline-skill.md) — converting advice into enforceable discipline.
- [`patterns/versioning.md`](../patterns/versioning.md) — version bumps and deprecation.
- [`reference/trigger-evals.md`](../reference/trigger-evals.md) — how to test routing after a migration.
- [`reference/evaluation-framework.md`](../reference/evaluation-framework.md) — full evaluation framework.
- [`patterns/portability.md`](../patterns/portability.md) — degradation and cross-harness compatibility.
