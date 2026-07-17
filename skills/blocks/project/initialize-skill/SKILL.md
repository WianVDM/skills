---
name: initialize-skill
description: First-run config initializer for any skill. Detects the project environment, loads skill-level defaults, merges them with existing project config, handles schema migration, proposes the result to the user, and persists it only after explicit approval.
invocation: model-invoked
depends:
  - detect-project-context
---

# initialize-skill

Tool building block: propose, and on approval write, a skill's project config.

## Contract

Merge `defaults < shared < skill` (each layer optional) into a proposal. Return the proposal with a changes summary. Write only the skill layer, only with `--approve HASH` matching the approved proposal. The caller owns user approval.

## In scope

Use when a consuming skill declares defaults in `config.yaml` and needs first-run setup, key backfill after an update, or schema migration.

Does: load, merge, backfill missing keys, type-check (advisory), propose, write on approval.

## Out of scope

Prompting the user, validating beyond types, secrets (`token-resolver`), writing `shared.yaml`, judging write safety.

## Operations

- `scripts/initialize.py` — propose; write with `--approve HASH`.
- `scripts/load-skill-config.py` — read-only merged load for normal operation.

Caller flow: resolve `marker_dir` via `detect-project-context` → run `initialize.py` → show the changes summary → on approval, re-run with `--approve` and the `proposal_hash`.

## Detail

- [Interface](references/INTERFACE.md) — inputs, outputs, exit codes, migration.
- [Config format](references/CONFIG_FORMAT.md) — the `config.yaml` declaration format.
- [Dependencies](references/DEPENDENCIES.md)
