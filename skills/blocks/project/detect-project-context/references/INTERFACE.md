# Interface

`detect-project-context` provides two scripts: `detect-project-context.py` and `resolve-standards-path.py`.

## `detect-project-context.py`

Detects the project root and recommended directories.

### Inputs

| Flag | Default | Description |
|---|---|---|
| `--start <dir>` | `.` | Directory to start searching from. |
| `--json` | off | Emit the full JSON report. Without it, a short human summary (root, marker, confidence, note, recommended dirs). |

### Algorithm

1. Resolve the start directory.
2. Search upward for a marker directory. The search **stops at the nearest VCS root** (`.git` file or directory); a marker above the repo is never used. If no marker exists at or below the VCS root, the VCS root is returned with `marker: null`.
3. Build candidate directories. Layout markers get `{root}/{marker}/{purpose}/` candidates; harness markers and VCS fallbacks get the standard `.agents` set.
4. Prefer existing directories; otherwise use the first candidate.
5. Emit the report.

### Markers

| Marker | Kind | Effect |
|---|---|---|
| `.agents` | layout | Root + `{marker}/{purpose}` candidates. |
| `.pi` | layout | Root + `{marker}/{purpose}` candidates. |
| `.claude`, `.codex`, `.cursor` | harness | Root only; standard `.agents` candidates, plus a `note`. |

Priority is the order above when several markers share one directory. A bare `agents` directory is **not** a marker (it false-positives on ordinary source folders), but `root/agents/skills` remains a candidate fallback.

### Output

```json
{
  "project_root": "/path/to/project",
  "marker": ".agents",
  "confidence": "high",
  "recommended_skills_dir": "/path/to/project/.agents/skills",
  "recommended_context_dir": "/path/to/project/.agents/context",
  "recommended_config_dir": "/path/to/project/.agents/config",
  "skills_dir_candidates": ["..."],
  "context_dir_candidates": ["..."],
  "config_dir_candidates": ["..."],
  "note": null
}
```

| Field | Meaning |
|---|---|
| `project_root` | Detected root, or `null` when nothing anchors the project. |
| `marker` | The marker that identified the root, or `null` on VCS fallback. |
| `confidence` | `high` — skills and context exist. `medium` — some expected directories exist. `low` — none exist, or the root fell back to VCS or home. |
| `recommended_*_dir` | Preferred directory per purpose (first existing candidate, else first candidate). |
| `*_dir_candidates` | All candidates per purpose, in preference order. |
| `note` | Why the answer is weakened (home directory, harness marker, VCS fallback). `null` on a clean detection. Callers should surface it to the user. |

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Detection returned. Check `confidence` and `note` before writing. |
| 2 | Invalid input (start path missing or not a directory). Error envelope: `{"status": "error", "errors": [...]}`. |

## `resolve-standards-path.py`

Resolves the canonical skill-standards path, per the `standards-path` architecture rule.

### Inputs

| Flag | Default | Description |
|---|---|---|
| `--start <dir>` | `.` | Directory to start project detection from. |
| `--standards-path <dir>` | — | Override; skips detection. |
| `--json` | off | Full JSON output. |

### Resolution order

1. `--standards-path` CLI override (validated).
2. `standards_path` from `{config_dir}/write-a-skill.yaml`. The PyYAML import is lazy; without it this layer is skipped with a `note`.
3. `{root}/{marker}/docs/skill-standards`.
4. `{root}/docs/skill-standards`, then `{root}/.agents/...`, then `{root}/.pi/...`.
5. Bundle default: first valid `docs/skill-standards` found walking up from the script.

A valid standards path contains `README.md` or a `fundamentals/` directory.

### Output

```json
{
  "status": "found",
  "standards_path": "/path/to/docs/skill-standards",
  "source": "cli | config | marker | project-root | project-root-agents | project-root-pi | bundle",
  "degraded": false,
  "note": "PyYAML not installed; skipped the config layer for standards_path."
}
```

On failure: `status: "missing"`, `degraded: true`, a `reason`, and `fallback_options` (`fetch`, `embedded`, `abort`) for the caller to present.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | `found`. |
| 1 | `missing` (degraded). |
| 2 | Invalid input. Error envelope: `{"status": "error", "errors": [...]}`. |
