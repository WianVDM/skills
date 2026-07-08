# Sync rules

The sync plan compares the source package `github.com/WianVDM/skills` to the installed skills in the target scope.

## Statuses

| Status | Definition | Default action |
|---|---|---|
| `missing` | Skill exists in source but not in target scope. | Install after confirmation. |
| `changed` | Skill exists in both but content differs. | Update after confirmation. |
| `identical` | Skill exists in both and content is the same. | Skip. |
| `modified` | Target copy differs from source; source version is newer or equal. | Conflict resolution. |
| `older` | Target version is newer than source. | Conflict resolution. |
| `target-only` | Skill exists in target but not in source. | Surface to the user; do not remove or modify. |

## Content comparison

Compare skill directories using `diff -r` or equivalent. If any difference exists, the installed copy is treated as locally modified.

## Version comparison

Use the `version` frontmatter field when present. If absent, fall back to content comparison. The default source version is the latest release of `github.com/WianVDM/skills`; a specific tag can be requested with `--version <tag>`.

## Generated-file exclusions

During comparison and copy, ignore generated or environment-specific files and directories. The `sync.excludes` rule covers, at minimum:

- `__pycache__`
- `*.pyc`
- `.DS_Store`
- `node_modules`
- `.git`

Any status decision must be based on the remaining content after these exclusions are applied.

## Conflict resolution

When a skill is `modified` or `older`, the user must choose an action:

| Action | Behavior |
|---|---|
| `backup, then overwrite` (recommended) | Copy the local skill to a backup location, then replace it with the source version. |
| `overwrite` | Replace the local skill with the source version without creating a backup. |
| `keep local` | Leave the local skill unchanged and skip it during this sync. |
| `skip` | Do not change this skill during this run. |

In preview mode, the proposed action is shown but no files are changed.

## Installation pattern

Before installing or updating skills, detect whether the existing skills in the target scope are installed as symlinks or as regular copies.

| Pattern | How to detect | Default action |
|---|---|---|
| Symlink | The skill directory or file is a symlink, or the target scope path is a symlink farm. | Ask the user; default to following the symlink pattern. |
| Copy | The skill directory is a regular directory or file. | Copy new and updated skills into the canonical target path. |

If any installed skill is a symlink, ask the user:

- **Follow the symlink pattern** (recommended): install or update skills as symlinks, matching the existing layout.
- **Install to the canonical target path**: copy skills directly into the resolved target directory.

The user's choice applies to the entire sync. Do not mix patterns within a single sync unless the user explicitly requests it.

## Backup location

Backups are written to `{context_dir}/setup-wian-skills/backups/<timestamp>/<skill-name>/`, where `{context_dir}` is the recommended context directory from `detect-project-context`. If a backup already exists, append a counter to the directory name.

## Rollback

If an install or update step fails, the skill rolls back any changes made during the current sync and restores the previous state from backups or the original installed versions.
