# Interface

`initialize-skill` provides two scripts: `initialize.py` and `load-skill-config.py`.

Merge precedence for both: `defaults < shared < skill`.

## `initialize.py`

Proposes and optionally writes a skill's project-level configuration.

### Inputs

Data fields accept CLI flags or a JSON object on stdin. CLI flags override stdin values.

| Field | CLI flag | Stdin key | Required | Description |
|---|---|---|---|---|
| `marker_dir` | `--marker-dir` | `marker_dir` | yes | Project marker directory (e.g., `.agents`). Must already exist. |
| `skill_name` | `--skill-name` | `skill_name` | yes | Name of the skill to initialize. |
| `skill_dir` | `--skill-dir` | `skill_dir` | no | Path to the skill directory containing `config.yaml`. If omitted, `defaults` must be provided. |
| `defaults` | `--defaults` | `defaults` | no | JSON object with default values. If omitted, `skill_dir` must be provided. |
| `schema_version` | `--schema-version` | `schema_version` | no | Expected config schema version; triggers migration if different. |

Control fields are CLI-only:

| Flag | Description |
|---|---|
| `--approve HASH` | Write the config. `HASH` must be the `proposal_hash` from the proposal the user approved. |
| `--json` | Emit machine-readable output. Without it, a human-readable summary is printed. |

Passing `approve` via stdin is rejected with an error. Writes require the flag.

### Outputs

JSON to stdout:

```json
{
  "status": "needs_approval" | "unchanged" | "written" | "error",
  "proposal_hash": "b7e2c1a9f04d3e88",
  "marker_dir": "...",
  "config_path": "...",
  "existing": true,
  "schema_version": "1.0.0",
  "changes": {
    "added": ["tools.ci.provider"],
    "preserved": ["tools.pr.provider"],
    "updated": ["schema_version"],
    "migrated_from": "0.9.0",
    "shadowed_shared": ["agents.context_dir"]
  },
  "missing_required": ["tools.notifications.channel"],
  "warnings": ["timeout must be an integer"],
  "proposed": { "...effective view, all layers merged..." },
  "write_set": { "...skill layer only; what gets persisted..." },
  "backup_path": "...",
  "errors": []
}
```

| Field | Meaning |
|---|---|
| `status` | `needs_approval` — proposal ready, nothing written. `unchanged` — existing config already matches; nothing to write. `written` — config persisted. `error` — see `errors`. |
| `proposal_hash` | Fingerprint of `write_set`. `--approve` refuses to write if the recomputed hash differs, so what was shown is what gets written. Shared-layer edits do not affect it. |
| `changes.added` | Leaf paths in `write_set` that are not in the existing config (backfill). |
| `changes.preserved` | Leaf paths where the existing config differs from defaults (user edits kept). |
| `changes.updated` | Leaf paths whose value would change (today: `schema_version` only). |
| `changes.migrated_from` | Previous `schema_version` when a migration occurs, else null. |
| `changes.shadowed_shared` | Leaf paths present in both the existing config and `shared.yaml`; the skill-layer copy shadows the shared value. Advisory only. |
| `missing_required` | Keys declared `required: true` in `config.yaml` with no value in any layer. Only populated when loading from `skill_dir`. The block never prompts; the caller decides. |
| `warnings` | Advisory type mismatches between defaults and the effective config. Never block a write. |
| `proposed` | Effective config: `defaults < shared < skill`. For display and type-checking. |
| `write_set` | Skill layer: `defaults < existing {skill}.yaml`, plus `schema_version` if provided. This — and only this — is persisted. Shared keys are never written. |
| `backup_path` | Timestamped backup of the previous config. Present only when overwriting. |

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Proposal returned (`needs_approval`/`unchanged`) or config written. |
| 1 | Runtime failure: missing marker directory, unreadable or unparseable config files, stale `proposal_hash`. |
| 2 | Invalid input: missing required fields, malformed JSON, `approve` via stdin, bad key prefix in `config.yaml`. |

### Example

```bash
# 1. Propose
python initialize.py \
  --marker-dir ./.agents \
  --skill-name pr-report \
  --skill-dir ./skills/main/workflow/pr-report \
  --schema-version 1.0.0 \
  --json

# 2. Caller shows the changes summary; the user approves.

# 3. Write, passing back the approved hash
python initialize.py \
  --marker-dir ./.agents \
  --skill-name pr-report \
  --skill-dir ./skills/main/workflow/pr-report \
  --schema-version 1.0.0 \
  --approve b7e2c1a9f04d3e88 \
  --json
```

## `load-skill-config.py`

Read-only config loader for normal skill operation. Safe to call at any time.

### Inputs

JSON on stdin:

```json
{
  "marker_dir": "<path>",
  "skill_name": "<name>",
  "defaults": { ... }
}
```

### Outputs

JSON to stdout:

```json
{
  "status": "ready" | "missing" | "error",
  "config": { ... },
  "shadowed_shared": ["agents.context_dir"],
  "errors": []
}
```

| Status | Meaning |
|---|---|
| `ready` | Config loaded from at least one source. |
| `missing` | No project config found; only defaults (if any) are in `config`. |
| `error` | Parsing, type, or I/O error. The merged config is still returned. |

`shadowed_shared` lists leaf paths present in both `shared.yaml` and `{skill}.yaml`. The skill-layer copy wins at those paths, so later `shared.yaml` updates are shadowed.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | `ready`. |
| 1 | `missing` or `error`. |
| 2 | Invalid input. |

## Schema migration

When `schema_version` is provided and differs from the existing config's version:

- Missing default keys are backfilled (`changes.added`).
- Existing user keys and values are preserved.
- `schema_version` is updated (`changes.migrated_from` records the old version).
- The migrated config is written only after `--approve HASH`.
