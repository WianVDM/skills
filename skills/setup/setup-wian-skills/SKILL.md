---
name: setup-wian-skills
description: Sync skills from github.com/WianVDM/skills, resolve shared configuration, and present the initialization checklist. Use when setting up or updating a workspace.
version: 1.0.1
invocation: user-invoked
license: Proprietary
metadata:
  author: Wian van der Merwe
  tags: [setup, conductor, bootstrap, sync, configuration, wian-skills]
depends:
  - detect-project-context
  - list-available-skills
  - install-skill
  - validate-skill-frontmatter
---

# Setup Wian's Skills

## Purpose

Sync skills from the canonical source package (`github.com/WianVDM/skills`) into the current workspace, resolve shared configuration keys once, and present a checklist for any skill-specific initialization.

## Type

Conductor.

## In scope

- Sync skills from `github.com/WianVDM/skills` into project or user scope.
- Resolve conflicts with locally modified or same-name skills.
- Gather shared configuration once, deduplicate keys, and infer answers from previous responses.
- Confirm the full plan before applying changes.
- Present the initialization checklist and write a context report.

## Out of scope

- Installing skills from sources other than `github.com/WianVDM/skills`. Use `install-skill` for that.
- Editing project-owned files such as `AGENTS.md`, `CLAUDE.md`, or `README.md`. Write context reports to the detected context directory instead of project-owned files.
- Running arbitrary scripts from skill directories without explicit approval.
- Modifying target-only skills. Surface them and do not change them.

## Quality guarantees

- No changes are applied without explicit user approval.
- The sync is applied atomically and rolled back if any step fails.
- Every installed or updated skill is validated after sync.

## When to use

- First time a workspace uses these skills.
- After the source package releases a new version.
- When a new shared configuration key must be resolved.
- Before a long work session to verify the workspace is on the latest skill versions.

## Branch entry

| Branch | Trigger | Outcome |
|---|---|---|
| **sync** | No `--preview` flag (default) | Run the full sync workflow. |
| **preview** | `/setup-wian-skills --preview` | Show the plan and configuration questions without applying changes. |

**Completion criterion:** the branch is one of {sync, preview} and the user has confirmed or corrected the default.

## Workflow

### 1. Pre-flight checks

Verify required capabilities before any network or disk operations:

- `detect-project-context`, `list-available-skills`, `install-skill`, and `validate-skill-frontmatter` are available.
- A network fetch tool is available (`git` preferred; `curl` as fallback).
- The workspace is trusted enough to read and write skill files; if not, stop.

**Completion criterion:** all required capabilities are present, or the skill stops and reports what is missing.

### 2. Resolve source and target

- Source is always `github.com/WianVDM/skills`.
- Determine the version to sync: latest release by default, or `--version <tag>` if supplied.
- Use `detect-project-context` to find the project root, the recommended config directory, and the recommended context directory.
- Ask whether to target project or user scope; resolve the canonical storage path for the chosen scope.

**Completion criterion:** source version, target scope, and canonical target path are resolved.

### 3. Discover and plan

Use `list-available-skills` to discover installed skills. For each installed skill, determine whether it is a symlink or a regular copy. If any installed skill is a symlink, ask the user which installation pattern to use for this sync:

- **Follow the symlink pattern** (recommended default): install or update skills as symlinks, matching the existing layout.
- **Install to the canonical target path**: copy skills directly into the resolved target directory, ignoring the symlink pattern.

Then fetch the source package and compare it to the installed inventory. Determine a status for each skill (`missing`, `changed`, `identical`, `modified`, `older`, or `target-only`). See [references/SYNC_RULES.md](references/SYNC_RULES.md) for status definitions.

**Completion criterion:** a sync plan exists with a status and proposed action for every skill, and the installation pattern is resolved.

### 4. Resolve conflicts

For every `modified` or `older` skill, ask per skill:

- **Backup, then overwrite** (recommended default)
- **Overwrite**
- **Keep local**
- **Skip**

In the **preview** branch, show the proposed resolution only.

**Completion criterion:** the user has chosen an action for every conflict, or the skill aborts.

### 5. Gather and prompt for configuration

Read `config.yaml` from every skill in the approved sync plan. Build a configuration graph per [references/CONFIG_DECLARATION.md](references/CONFIG_DECLARATION.md):

- Collect, deduplicate, and infer `shared` keys.
- Preserve existing values from the shared config file.
- Ask one question at a time for each unresolved key, allowing earlier answers to unlock, skip, or rephrase later questions.

In the **preview** branch, list the questions that would be asked; do not prompt.

**Completion criterion:** every required key has a value, or the skill stops and explains what is missing.

### 6. Confirm the full plan

Present the complete plan for explicit approval: source version, target scope, skills to change, conflict resolutions, backup locations, config keys to write, and skills requiring initialization. If the user declines, abort without writing files.

**Completion criterion:** the user has approved the plan.

### 7. Apply and validate

Use `install-skill` to copy each approved skill into the target scope, or create symlinks if the user chose the symlink pattern. Apply changes in an order that allows rollback:

- Back up locally modified skills before overwriting if the user chose that option.
- Install or update each skill using the resolved pattern (symlink or copy).
- If any step fails, roll back to the pre-sync state.
- Run `validate-skill-frontmatter` on every installed or updated skill and record the results.

In the **preview** branch, skip this phase entirely.

**Completion criterion:** approved skills are installed and validated, or the workspace is rolled back.

### 8. Finalize

- Write the resolved shared config, preserving existing unchanged keys.
- Present the initialization checklist for skills with `requires_setup: true` or an `## Initialization` section.
- Write a context report to `{context_dir}/setup-wian-skills/last-sync.md`, where `{context_dir}` is the recommended context directory from `detect-project-context`, summarizing the sync, backups, config changes, validation results, and next steps.

In the **preview** branch, skip this phase.

**Completion criterion:** shared config is written, the checklist is displayed, and the context report is written.

## Failure handling

- Missing required dependency or source fetch failure: stop and report what is missing.
- User declines the sync plan or a required config key: abort without writing files.
- Sync step failure during apply: roll back to the pre-sync state and report the failure.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Config declaration format](references/CONFIG_DECLARATION.md)
- [Sync rules](references/SYNC_RULES.md)
- [Initialization checklist format](references/CHECKLIST.md)
- [Default source configuration](references/DEFAULTS.md)
- [Dependencies](references/DEPENDENCIES.md)
