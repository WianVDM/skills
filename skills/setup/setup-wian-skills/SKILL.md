---
name: setup-wian-skills
description: Initialize and set up configuration for Wian's skills in the workspace. Resolve shared configuration once across installed bundle skills — fully now, or deferred to lazy first-use loading — and present the initialization checklist. Use after installing the WianVDM/skills bundle, when the user says they just installed it, when a configuration key must be resolved, or when the user asks to set up or reinitialize skill configuration.
invocation: user-invoked
depends:
  - detect-project-context
  - list-available-skills
  - initialize-skill
  - context-reports
---

# Setup Wian's Skills

## Purpose

Prepare the workspace's configuration so Wian's skills work properly. The skill resolves shared configuration once across all installed bundle skills and presents the initialization checklist. It never installs, updates, syncs, or removes skills — installation is the user's action, configuration is this skill's action.

## Type

Conductor.

## In scope

- Detect the workspace context: project root, recommended config directory, recommended context directory.
- Discover installed bundle skills and read their `config.yaml` declarations.
- Build the cross-skill configuration graph: deduplicate `shared` keys, apply `${ref}` inference, order questions through `depends_on`.
- Resolve `shared` keys — the bindings to the global shared config — in every branch.
- Resolve skill-private keys now (**full** branch) or defer them to first-use lazy loading (**lazy** branch) when the skill is lazy-eligible.
- Confirm the plan before writing; write `shared.yaml` directly; delegate per-skill config writes to `initialize-skill`.
- Present the initialization checklist.
- Write a context report.

## Out of scope

- Installing, updating, syncing, or removing skills. If no bundle skills are installed, stop and hand the user the install command from [references/DEFAULTS.md](references/DEFAULTS.md). A dedicated sync skill is planned.
- Manually fetching or copying skills from the source package.
- Editing project-owned files such as `AGENTS.md`, `CLAUDE.md`, or `README.md`.
- Running arbitrary scripts from skill directories without explicit approval.
- Modifying target-only skills. Surface them and do not change them.
- Prompting, in the **lazy** branch, for configuration that a lazy-eligible skill can resolve on first use.

## When to use

- After the `WianVDM/skills` bundle is installed in the workspace, including when the user says they just installed it.
- First time a workspace uses these skills.
- When a new shared configuration key must be resolved.
- When the user wants to reinitialize shared configuration.

## Branch entry

Ask the user first: run the full setup now, or defer to lazy loading? Recommend **lazy** — bundle skills are assumed to follow the lazy-loading pattern, and deferring avoids asking questions for skills the user may never run. Recommend **full** when the user wants everything settled in one pass.

| Branch | Trigger | Outcome |
|---|---|---|
| **lazy** | `/setup-wian-skills` → user chooses defer (recommended default) | Resolve shared keys now; defer skill-private keys of lazy-eligible skills to first use. |
| **full** | `/setup-wian-skills` → user chooses full setup | Resolve all shared and skill-private keys now. |
| **preview** | `/setup-wian-skills --preview` | Show the plan and the questions each mode would ask, without writing anything. |

**Completion criterion:** the branch is one of {lazy, full, preview} and the user has confirmed or corrected the default.

## Workflow

### 1. Pre-flight checks

- `detect-project-context`, `list-available-skills`, and `initialize-skill` are available.
- The workspace is trusted enough to read skill files and write config files; if not, stop.

**Completion criterion:** all required capabilities are present, or the skill stops and reports what is missing.

### 2. Resolve context and scope

- Use `detect-project-context` to find the project root, the recommended config directory, and the recommended context directory. If detection returns low confidence, ask the user to confirm the paths before continuing.
- Ask whether to target project or user scope; resolve the canonical storage path for the chosen scope.

**Completion criterion:** target scope and canonical config path are resolved.

### 3. Discover bundle skills

Use `list-available-skills` to discover installed skills, and determine which ones belong to the `WianVDM/skills` bundle per the identity in [references/DEFAULTS.md](references/DEFAULTS.md). When bundle membership comes from the name-matching fallback rather than lock metadata, confirm the resulting set with the user before continuing.

- If no bundle skills are installed, stop. Report that nothing is installed and hand back the exact install command from DEFAULTS.md for the user to run themselves. Do not install anything.

**Completion criterion:** the set of installed bundle skills is known, or the skill has stopped with the install command reported.

### 4. Build the configuration graph

Read `config.yaml` from every discovered bundle skill. Build the graph per [references/CONFIG_DECLARATION.md](references/CONFIG_DECLARATION.md):

- Collect and deduplicate `shared` keys; apply `${ref}` inference; order questions through `depends_on`.
- Classify each skill: **lazy-eligible** if its `SKILL.md` contains an `## Initialization` section, not eligible otherwise.
- Classify each key into the resolve-now set or the deferrable set:
  - `shared` keys always resolve now.
  - Skill-private keys with `bootstrap: true` always resolve now.
  - Skill-private keys on lazy-eligible skills defer in the **lazy** branch and resolve now in the **full** branch.
  - Skill-private keys on skills that are not lazy-eligible resolve now in both branches.

**Completion criterion:** the graph exists, every key is classified, and lazy eligibility is recorded per skill.

### 5. Prompt for configuration

- Preserve existing values from the shared config file and per-skill config files.
- Ask one question at a time for each unresolved key in the resolve-now set, allowing earlier answers to unlock, skip, or rephrase later questions.
- In the **lazy** branch, ask only the resolve-now set. In the **full** branch, ask everything.
- In the **preview** branch, list the questions each mode would ask; do not prompt.

This skill owns only the cross-skill graph: dedupe of `shared` keys, `${ref}` inference, and question ordering. Delegate per-skill config mechanics — loading skill defaults, merging with existing project config, schema migration, and persisting after approval — to `initialize-skill`.

**Completion criterion:** every required key in the resolve-now set has a value, or the skill stops and explains what is missing.

### 6. Confirm the plan

Present the complete plan for explicit approval: keys resolved now with their proposed values, keys deferred with the per-skill lazy list, files to write (`shared.yaml` plus each skill config touched), and the checklist contents. In the **preview** branch, present the plan for both modes without requesting approval. If the user declines, abort without writing files.

**Completion criterion:** the user has approved the plan.

### 7. Write configuration

- Write resolved `shared` keys to `{config_dir}/shared.yaml`, preserving existing unchanged keys.
- For every skill with keys in the resolve-now set, delegate to `initialize-skill`: load defaults, merge, propose, and write the skill layer only after the user approves its proposal.

In the **preview** branch, skip this phase entirely.

**Completion criterion:** `shared.yaml` and every approved skill config are written, or the workspace is unchanged.

### 8. Finalize

- Present the initialization checklist per [references/CHECKLIST.md](references/CHECKLIST.md): the configured-now list and, in the **lazy** branch, the self-configures-on-first-use list.
- Write a context report per the `context-reports` conventions to `{context_dir}/setup/last.md`, where `{context_dir}` is the recommended context directory from `detect-project-context`, summarizing the branch, keys resolved and deferred, files written, and next steps.

In the **preview** branch, skip this phase.

**Completion criterion:** the checklist is displayed and the context report is written.

## Failure handling

- Missing required dependency: stop and report what is missing.
- No bundle skills installed: stop and hand back the install command; write nothing.
- User declines the plan or a required `shared` key has no value: abort without writing files.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Config declaration format](references/CONFIG_DECLARATION.md)
- [Initialization checklist format](references/CHECKLIST.md)
- [Bundle identity and install command](references/DEFAULTS.md)
- [Dependencies](references/DEPENDENCIES.md)
