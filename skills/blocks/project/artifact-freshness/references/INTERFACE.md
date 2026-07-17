# Interface

`artifact-freshness` exposes one script: `scripts/check-freshness.py`.

## Inputs

Either CLI flags or a JSON object on stdin. CLI flags override stdin values.

### CLI

```bash
python check-freshness.py --report <path> [options]
python check-freshness.py --observation <json> [options]
```

| Flag | Description |
|---|---|
| `--report` | Path to the markdown report to check. |
| `--observation` | JSON string with a chainlog observation entry. |
| `--branch` | Current branch. Auto-detected from git if omitted. |
| `--commit` | Current commit. Auto-detected from git if omitted. |
| `--source-updated-at` | Timestamp when the underlying source was last updated. |
| `--freshness-hours` | Maximum age in hours. |
| `--schema-version` | Expected schema version. |
| `--cwd` | Project root directory. Default: current working directory. |
| `--json` | Emit machine-readable output. |

### Stdin JSON

```json
{
  "mode": "report" | "observation",
  "report_path": "/path/to/report.md",
  "report_frontmatter": { ... },  // optional; used instead of reading the file
  "observation": { ... },
  ...
}
```

Dimensions are evaluated only when there is something to compare. `schema_version` is evaluated only when the caller passes `--schema-version`: an artifact that declares a schema version is not judged stale just because the caller did not ask.

If `report_frontmatter` is provided, it is used instead of parsing the file at `report_path`. This avoids re-parsing when the caller already has the frontmatter.

## Output

JSON to stdout:

```json
{
  "fresh": true | false,
  "reason": "...",
  "dimensions": {
    "branch": { "fresh": true | false, "reason": "...", "report_branch": "...", "current_branch": "..." },
    "commit": { "fresh": true | false, "reason": "...", "report_commit": "...", "current_commit": "..." },
    "source_timestamp": { "fresh": true | false, "reason": "...", "source_updated_at": "...", "artifact_source_updated_at": "..." },
    "generated_timestamp": { "fresh": true | false, "reason": "...", "artifact_generated_at": "...", "last_commit_at": "..." },
    "schema_version": { "fresh": true | false, "reason": "...", "expected_schema_version": "...", "artifact_schema_version": "..." },
    "age": { "fresh": true | false, "reason": "...", "artifact_generated_at": "...", "age_hours": 1.5, "threshold_hours": 24 }
  }
}
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | The artifact is fresh. |
| 1 | The artifact is stale, or a runtime error occurred. |
| 2 | Invalid input (malformed JSON, missing mode). |

Verdicts use the `fresh`/`reason`/`dimensions` shape. Invalid input and runtime failures use the standard error envelope: `{"status": "error", "errors": [...]}`.

## Report frontmatter fields

The script recognizes these frontmatter fields (case-insensitive keys):

| Canonical field | Aliases |
|---|---|
| `artifact_branch` | `artifact_branch`, `branch`, `report_branch` |
| `artifact_commit` | `artifact_commit`, `commit`, `report_commit` |
| `artifact_generated_at` | `artifact_generated_at`, `generated_at`, `updated_at`, `created_at`, `collected_at` |
| `artifact_source_updated_at` | `artifact_source_updated_at`, `source_updated_at`, `ticket_updated_at` |
| `artifact_schema_version` | `artifact_schema_version`, `schema_version`, `schema` |

## Chainlog observation fields

Chainlog observations are checked against these fields:

| Canonical field | Aliases |
|---|---|
| `artifact_branch` | `branch`, `artifact_branch` |
| `artifact_commit` | `commit`, `artifact_commit` |
| `artifact_generated_at` | `collected_at`, `generated_at`, `updated_at`, `created_at` |
| `artifact_source_updated_at` | `source_updated_at`, `ticket_updated_at` |
| `artifact_schema_version` | `schema_version`, `schema` |

## Examples

Check a report:

```bash
python check-freshness.py --report .agents/context/debrief/OC-1234.md --json
```

Check a chainlog observation:

```bash
python check-freshness.py --observation '{"collected_at": "2026-07-14T10:00:00Z", "commit": "abc1234"}' --commit abc1234 --json
```
