---
name: setup-wian-skills
description: Set up or update Wian's skills in the workspace. Use the Vercel skills CLI to install or update the WianVDM/skills bundle, then resolve shared configuration once and present the initialization checklist.
version: 1.1.0
invocation: user-invoked
depends:
  - detect-project-context
  - list-available-skills
  - validate-skill-frontmatter
---

# Setup Wian's Skills

## Purpose

Prepare the workspace to use Wian's skills. The skill delegates installation and updates to the Vercel skills CLI, then resolves shared configuration once and presents the initialization checklist.

## Type

Conductor.

## In scope

- Install or update the `WianVDM/skills` bundle via the Vercel skills CLI.
- Detect the workspace context and choose the target scope.
- Warn about locally modified skills before the CLI overwrites them.
- Gather shared configuration once, deduplicate keys, and infer answers from previous responses.
- Confirm the full plan before applying changes.
- Present the initialization checklist.
- Write a context report.

## Out of scope

- Installing skills from sources other than `WianVDM/skills`. Use `install-skill` for that.
- Manually fetching or copying skills from the source package when the Skills CLI is available.
- Editing project-owned files such as `AGENTS.md`, `CLAUDE.md`, or `README.md`.
- Running arbitrary scripts from skill directories without explicit approval.
- Modifying target-only skills. Surface them and do not change them.

## Quality guarantees

- No changes are applied without explicit user approval.
- The Skills CLI is used for installation and updates; the skill does not invent harness-specific paths.
- Every installed or updated skill is validated after sync.

## When to use

- First time a workspace uses these skills.
- After the source package releases a new version.
- When a new shared configuration key must be resolved.
- Before a long work session to verify the workspace is on the latest skill versions.
- When the user only wants to reinitialize shared configuration without reinstalling skills.

## Branch entry

| Branch | Trigger | Outcome |
|---|---|---|
| **setup** | `/setup-wian-skills` (default) | Install or update the bundle, then resolve shared config and present the checklist. |
| **configure** | `/setup-wian-skills --configure` | Skip installation; only resolve shared config and present the checklist. |
| **preview** | `/setup-wian-skills --preview` | Show the plan and configuration questions without applying changes. |

**Completion criterion:** the branch is one of {setup, configure, preview} and the user has confirmed or corrected the default.

## Workflow

### 1. Pre-flight checks

Verify required capabilities before any network or disk operations:

- `detect-project-context`, `list-available-skills`, and `validate-skill-frontmatter` are available.
- The Vercel skills CLI is available (`npx` or `npm`). If not, stop and explain how to install Node.js/npm.
- The workspace is trusted enough to read and write skill files; if not, stop.

**Completion criterion:** all required capabilities are present, or the skill stops and reports what is missing.

### 2. Resolve source and target

- Source is always `WianVDM/skills` via the Vercel skills CLI.
- Determine the version to sync: latest release by default, or `--version <tag>` if supplied.
- Use `detect-project-context` to find the project root, the recommended config directory, and the recommended context directory.
- Ask whether to target project or user scope; resolve the canonical storage path for the chosen scope.

**Completion criterion:** source version, target scope, and canonical target path are resolved.

### 3. Discover and plan

Use `list-available-skills` to discover installed skills. Determine which skills are already present and which will be affected by the CLI install/update.

- In the **setup** branch, plan to run the CLI and then configure.
- In the **configure** branch, skip the CLI step.
- In the **preview** branch, show the proposed plan and configuration questions without applying changes.

**Completion criterion:** a plan exists for the chosen branch and the user has seen it.

### 4. Resolve conflicts

For every installed skill that will be touched by the CLI, warn the user if local modifications exist and ask whether to proceed:

- **Backup, then proceed** (recommended default)
- **Proceed without backup**
- **Keep local**
- **Skip**

In the **preview** branch, show the proposed resolution only.

**Completion criterion:** the user has chosen an action for every conflict, or the skill aborts.

### 5. Gather and prompt for configuration

Read `config.yaml` from every skill in the approved plan. Build a configuration graph per [references/CONFIG_DECLARATION.md](references/CONFIG_DECLARATION.md):

- Collect, deduplicate, and infer `shared` keys.
- Preserve existing values from the shared config file.
- Ask one question at a time for each unresolved key, allowing earlier answers to unlock, skip, or rephrase later questions.

In the **preview** branch, list the questions that would be asked; do not prompt.

**Completion criterion:** every required key has a value, or the skill stops and explains what is missing.

### 6. Confirm the full plan

Present the complete plan for explicit approval: source version, target scope, CLI command to run, conflict resolutions, backup locations, config keys to write, and skills requiring initialization. If the user declines, abort without writing files.

**Completion criterion:** the user has approved the plan.

### 7. Apply and validate

In the **setup** branch, run the Skills CLI command to install or update the bundle.

- If the CLI step fails, stop and report the failure without writing config.
- Back up locally modified skills before proceeding if the user chose that option.
- Run `validate-skill-frontmatter` on every installed or updated skill and record the results.

In the **configure** branch, skip the CLI step.
In the **preview** branch, skip this phase entirely.

**Completion criterion:** approved skills are installed and validated, or the workspace is unchanged.

### 8. Finalize

- Write the resolved shared config, preserving existing unchanged keys.
- Present the initialization checklist for skills with `requires_setup: true` or an `## Initialization` section.
- Write a context report to `{context_dir}/setup-wian-skills/last-sync.md`, where `{context_dir}` is the recommended context directory from `detect-project-context`, summarizing the CLI command, backups, config changes, validation results, and next steps.

In the **preview** branch, skip this phase.

**Completion criterion:** shared config is written, the checklist is displayed, and the context report is written.

## Failure handling

- Missing required dependency or Skills CLI failure: stop and report what is missing.
- User declines the setup plan or a required config key: abort without writing files.
- CLI install/update failure: stop and report the failure.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Config declaration format](references/CONFIG_DECLARATION.md)
- [Initialization checklist format](references/CHECKLIST.md)
- [Default source configuration](references/DEFAULTS.md)
- [Dependencies](references/DEPENDENCIES.md)
