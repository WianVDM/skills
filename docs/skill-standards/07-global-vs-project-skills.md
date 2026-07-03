# 07 — Global vs project-specific skills

A skill can be built for one project or built to work across any project, user, and harness. The difference is not just portability — it is pluggability. A global skill must drop into an unknown environment and still behave correctly.

---

## Project-specific skills

A project-specific skill lives inside a single project. It can assume things about that project: tools, conventions, file paths, APIs, issue trackers, domain language.

**When to use**

- The domain is tightly coupled to the project's architecture or workflow.
- The skill encodes a convention that only exists in this repo.
- The maintenance cost of generalizing outweighs the reuse value.

**Characteristics**

- Can hardcode project-specific paths, tools, or APIs.
- Should still declare its assumptions.
- Should still follow structural and compositional standards.

---

## Global skills

A global skill is designed to work in any project, with any user, in any harness. It must be **pluggable**: it detects the environment, adapts through config, and fails explicitly when a required capability is missing.

**What pluggable means**

A global skill should be able to:

- Run in a repo it has never seen before.
- Work with different issue trackers, test runners, package managers, and VCS workflows.
- Adapt to user preferences without changing its core contract.
- Declare every assumption, dependency, and required capability.
- Fail closed when a required capability is missing.

Pluggability is not the absence of assumptions. It is the explicit handling of assumptions.

---

## What makes a skill truly global

### 1. Harness-agnostic language

The skill must not assume a specific agent harness, tool name, slash command, or vendor API.

| Project-specific | Global |
|-----------------|--------|
| Run `/ticket OC-1234`. | Invoke the ticket-research skill for ticket OC-1234. |
| Call the `Agent` tool. | Spawn a focused worker. |
| Use `git status`. | Check the current working state. |

If a harness-specific detail is unavoidable, isolate it in a clearly labeled reference file.

### 2. Project-agnostic conventions

The skill must not hardcode project-specific tools, paths, or APIs.

| Project-specific | Global |
|-----------------|--------|
| Open Jira ticket PROJ-123. | Open the configured issue tracker for ticket PROJ-123. |
| Run `npm test`. | Run the project's test command. |
| Read `src/app/config.ts`. | Read the project's configuration entry point. |

The skill should detect the environment, consult config, or ask the user.

### 3. Explicit dependencies

A global skill must declare:

- Other skills it expects to be available.
- External tools, APIs, MCP servers, or extensions it requires.
- Specific scripts, files, or conventions it relies on.
- Environment variables or secure stores it references.

Dependencies are not bad. Hidden dependencies are.

### 4. Self-configuration through detection

A global skill should detect as much as possible before asking the user. Detection reduces friction and makes the skill pluggable.

Examples:

- Detect the issue tracker from `git remote`, repo files, or existing config.
- Detect the test command from `package.json`, `pyproject.toml`, or similar.
- Detect the project structure before assuming a monolith or monorepo.

Only ask the user when detection is ambiguous or insufficient.

### 5. User preferences without core changes

A global skill adapts to user preferences through config and notes, not by changing its core contract. The core stays stable; the config layer changes.

See [09-configuration.md](./09-configuration.md) for the config pattern.

### 6. Fail closed

If a required capability is missing, the skill stops and explains what is missing. It does not guess or proceed with a degraded fallback unless the user has explicitly approved that fallback.

---

## The pluggability checklist

Before calling a skill global, check:

- [ ] It contains no project-specific paths or tool names in `SKILL.md`.
- [ ] It detects the environment where possible.
- [ ] It declares all required skills, tools, APIs, and environment variables.
- [ ] It uses config and notes for preferences, not hardcoded values.
- [ ] It fails closed when a required capability is missing.
- [ ] It does not assume a specific agent harness or slash-command convention.
- [ ] Its outputs are useful in a project the author has never seen.

---

## Migrating from project-specific to global

Most skills start project-specific. To make one global:

1. Replace hardcoded paths and tools with detection or config.
2. Extract project-specific reference into config or a separate project-specific skill.
3. Declare dependencies explicitly.
4. Test the skill in a clean project it has never seen.
5. Document the migration path and any breaking changes.

A skill does not have to be global to be good. But if you intend it to be global, pluggability is non-negotiable.
