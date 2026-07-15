# Interface

`initialize-skill` provides two scripts: `initialize.py` and `load-skill-config.py`.

## `initialize.py`

Proposes and optionally writes a skill's project-level configuration.

### Inputs

Either CLI flags or a JSON object on stdin. CLI flags override stdin values.

| Field | CLI flag | Stdin key | Required | Description |
|---|---|---|---|---|
| `marker_dir` | `--marker-dir` | `marker_dir` | yes | Project marker directory (e.g., `.agents`). |
| `skill_name` | `--skill-name` | `skill_name` | yes | Name of the skill to initialize. |
| `skill_dir` | `--skill-dir` | `skill_dir` | no | Path to the skill directory containing `config.yaml`. If omitted, `defaults` must be provided. |
| `defaults` | `--defaults` | `defaults` | no | JSON object with default values. If omitted, `skill_dir` must be provided. |
| `schema_version` | `--schema-version` | `schema_version` | no | Expected config schema version; triggers migration if older. |
| `approve` | `--approve` | `approve` | no | If true, write the config. Default false. |
| `json` | `--json` | n/a | no | Emit machine-readable JSON output. Default false. |

### Outputs

JSON to stdout:

```json
{
  "status": "needs_approval" | "written" | "error",
  "marker_dir": "...",
  "config_path": "...",
  "existing": true | false,
  "changed": true | false,
  "schema_version": "...",
  "proposed": { ... },
  "backup_path": "...",      // only when writing an existing config
  "errors": []
}
```

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Proposal returned or config written successfully. |
| 1 | Error in proposal or write failed. |
| 2 | Invalid input. |

### Example

```bash
python initialize.py \
  --marker-dir ./.agents \
  --skill-name pr-report \
  --skill-dir ./skills/main/workflow/pr-report \
  --schema-version 1.0.0
```

Output:

```json
{
  "status": "needs_approval",
  "marker_dir": ".../.agents",
  "config_path": ".../.agents/config/pr-report.yaml",
  "existing": false,
  "changed": true,
  "schema_version": "1.0.0",
  "proposed": {
    "tools": { ... },
    "schema_version": "1.0.0"
  },
  "errors": []
}
```

## `load-skill-config.py`

Read-only config loader. Safe to call at any time.

### Inputs

JSON on stdin:

```json
{
  "marker_dir": "<path>",
  "skill_name": "<name>",
  "defaults": { ... }   // optional
}
```

### Outputs

JSON to stdout:

```json
{
  "status": "ready" | "missing" | "error",
  "config": { ... },
  "errors": []
}
```

| Status | Meaning |
|---|---|
| `ready` | Config loaded from at least one source. |
| `missing` | Only defaults were available; no project config found. |
| `error` | Parsing, type, or I/O error. |

### Exit codes

| Code | Meaning |
|---|---|
| 0 | `ready`. |
| 1 | `missing` or `error`. |
| 2 | Invalid input. |

### Example

```bash
python load-skill-config.py <<EOF
{
  "marker_dir": "./.agents",
  "skill_name": "pr-report",
  "defaults": {"tools": {"pr": {"provider": "auto"}}}
}
EOF
```

## Merge precedence

Both scripts merge config in the same order:

1. Skill-level defaults (from `config.yaml` or `--defaults`).
2. `{marker_dir}/config/shared.yaml` (overrides defaults).
3. `{marker_dir}/config/{skill}.yaml` (overrides shared and defaults).

## Schema migration

When `schema_version` is provided:

- If the existing config has a different `schema_version`, the block adds any missing default keys and updates the version.
- Existing user keys are preserved.
- The config is written only after `--approve`.
