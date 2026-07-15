---
name: initialize-skill
description: First-run config initializer for any skill. Detects the project environment, loads skill-level defaults, merges them with existing project config, handles schema migration, proposes the result to the user, and persists it only after explicit approval.
version: 1.0.0
invocation: model-invoked
depends:
  - detect-project-context
  - worker-contract
  - context-reports
---

# initialize-skill

## Purpose

Provide a reusable first-run configuration step for any skill that needs project-level settings. The block loads defaults from the skill's `config.yaml`, merges them with the project's `shared.yaml` and `{skill}.yaml`, handles schema migration, and writes the final config only after explicit approval.

## Skill type

Building block. It does not conduct research, make decisions, or ask the user questions. It only reads, merges, proposes, and writes config.

## When to use

A skill should use `initialize-skill` when:

- It has configurable project-level settings in a `config.yaml`.
- It needs a one-time setup step on first run in a project.
- It wants to preserve user edits across skill updates.
- It needs to migrate older config schemas to newer ones.

## In scope

- Load skill-level defaults from the consuming skill's `config.yaml`.
- Load `{config_dir}/shared.yaml` if present.
- Load `{config_dir}/{skill}.yaml` if present.
- Merge configs with the precedence: defaults < shared < skill-specific.
- Add missing default keys when the existing config is older or incomplete.
- Propose the final config without writing it.
- Write the config only when explicit approval is provided.
- Type-check merged values against defaults.

## Out of scope

- Complex per-key validation beyond type checking.
- Prompting the user for missing values.
- Resolving secrets or tokens (use `token-resolver`).
- Deciding whether a config change is safe (the caller owns that).

## Core contract

Accepts a marker directory, skill name, and defaults. Returns the proposed project-level config and writes it only when `--approve` is passed. The caller must obtain explicit user approval before invoking with `--approve`.

## Operations

Two scripts are provided:

- `scripts/initialize.py` — propose and optionally write project config.
- `scripts/load-skill-config.py` — read-only config loader for normal skill operation.

See [references/INTERFACE.md](references/INTERFACE.md) for full input/output schemas and examples.

## Workflow

1. The caller detects the project context with `detect-project-context` and obtains `marker_dir`.
2. The caller invokes `initialize.py` with the skill name and optional defaults.
3. The block loads existing config files and merges them with defaults.
4. The block returns the proposed config with `status: needs_approval`.
5. The caller shows the proposed config to the user and asks for approval.
6. If approved, the caller invokes `initialize.py` again with `--approve`.
7. The block writes `{config_dir}/{skill}.yaml` and returns `status: written`.

During normal operation, the caller invokes `load-skill-config.py` to read the merged config without writing.

## Config format

Consuming skills declare their defaults in a `config.yaml` using the format documented in [references/CONFIG_FORMAT.md](references/CONFIG_FORMAT.md).

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Interface](references/INTERFACE.md)
- [Config format](references/CONFIG_FORMAT.md)
- [Dependencies](references/DEPENDENCIES.md)
