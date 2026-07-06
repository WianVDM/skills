---
name: setup-wian-skills
description: Sync skills from a source package and resolve shared project configuration once. Run when setting up or updating a workspace.
version: 1.0.0
invocation: user-invoked
license: Proprietary
metadata:
  author: Wian van der Merwe
  tags: [setup, bootstrap, skills, configuration]
  verification_level: declared
---

# Setup Wian's Skills

## Purpose

Sync skills from a source package into a project or user scope, collect shared configuration once, and present a checklist for skill-specific initialization.

## Type

Conductor.

## In scope

- Sync skills from a configured source package into project or user scope.
- Detect local modifications and ask before overwriting.
- Collect shared configuration keys once and write them to the shared config file.
- Present a checklist of skills that need skill-specific initialization.
- Write a context report summarizing the sync and configuration state.

## Out of scope

- Editing project-owned files such as `AGENTS.md`, `CLAUDE.md`, or `README.md`. Write context reports to `.agents/context/` instead.
- Running arbitrary scripts from skill directories without explicit user approval. Require approval for each script execution.
- Installing skills from arbitrary third-party sources. Use only the configured source package.

## When to use

- First time a workspace uses these skills.
- After the source package changes and the workspace needs updates.
- When a new shared configuration key must be resolved.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## Workflow

### 1. Resolve scope and source

Detect the project root and ask whether to target project scope or user scope. Determine the source package from the configured default or from a user-supplied argument.

When targeting user scope, resolve the path to its canonical storage location before comparing or installing skills. See [Default source configuration](references/DEFAULTS.md) for symlink-farm guidance.

**Completion criterion:** scope, source, and canonical target path are resolved.

### 2. Discover installed skills

Use `list-available-skills` to find skills already present in the target scope.

**Completion criterion:** an inventory of installed skills exists.

### 3. Build and confirm sync plan

Fetch the source package, compare it to the installed inventory, and build a plan:

- install missing skills
- update changed skills
- skip identical skills
- flag locally modified skills for confirmation
- surface `target-only` skills without changing them
- ignore generated files listed in `sync.excludes` when comparing content

Present the plan and confirm before applying.

**Completion criterion:** user has approved the sync plan.

### 4. Apply sync

Use `install-skill` to copy each approved skill into the target scope.

**Completion criterion:** approved skills are installed.

### 5. Resolve shared configuration

Read `config.yaml` from each installed skill. Collect unique `shared` keys. For each missing shared key, prompt once using its default; do not batch all missing keys into a single prompt. Write the shared config file.

If a required key cannot be resolved and has no default, stop and explain what is missing.

**Completion criterion:** shared config is written and every missing key has been individually prompted and resolved.

### 6. Present initialization checklist

Identify skills that declare `requires_setup: true` in `config.yaml` or have an `Initialization` section. Present them as a checklist for the user to run.

**Completion criterion:** checklist is displayed and the user knows the next commands.

### 7. Write context report

Write a summary to `.agents/context/setup-wian-skills/last-sync.md`.

**Completion criterion:** context report is written.

## Failure handling

If the source package cannot be fetched, stop and report the failure. If a required dependency is missing, stop and list what is missing. If the user declines the sync plan, abort without writing files.

## References

- [Config declaration format](references/CONFIG_DECLARATION.md)
- [Sync rules](references/SYNC_RULES.md)
- [Initialization checklist format](references/CHECKLIST.md)
- [Default source configuration](references/DEFAULTS.md)
- [Dependencies](references/DEPENDENCIES.md)
