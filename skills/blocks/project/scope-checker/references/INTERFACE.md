# Interface

`scope-checker` exposes one subagent: `subagents/scope-checker.md`.

## Input

The parent skill embeds the following in the subagent prompt.

### `scope` envelope

| Field | Required | Description |
|---|---|---|
| `type` | yes | One of `ticket`, `pr`, `branch`, `commit`, `manual`. |
| `source` | yes | Primary scope description (ticket body, PR body, or manual text). |
| `title` | no | Short title of the scope. |
| `body` | no | Longer body of the scope. |
| `acceptance_criteria` | no | List of acceptance criteria strings. |
| `changed_files` | no | List of changed file paths in this work item. |
| `key` | no | Work-item key (e.g., `OC-1234` or `42`). |
| `url` | no | Source URL. |

### `findings` item

| Field | Required | Description |
|---|---|---|
| `id` | yes | Unique identifier for the finding. |
| `message` | yes | The finding text. |
| `source` | no | Source type (`human_reviewer`, `automated_reviewer`, `static_analysis`, `ci_failure`, etc.). |
| `severity` | no | Original severity (`blocker`, `required`, `required_to_resolve`, `recommended`, `informational`). |
| `file` | no | File path referenced by the finding. |
| `line` | no | Line number referenced. |
| `rule` | no | Rule or convention reference. |

### `project_conventions`

Optional array of strings or convention references to consider as part of the scope.

## Output

The subagent returns the standard `worker-contract` format. The `Findings` section contains:

### `classified` item

| Field | Description |
|---|---|
| `id` | The input finding id. |
| `classification` | One of `in-scope`, `out-of-scope`, `ambiguous`. |
| `reason` | Concise explanation. |
| `flags` | Optional tags (`scope-drift`, `unrelated`, `touches-unchanged-file`, `no-acceptance-criteria-match`). |

### `summary`

| Field | Description |
|---|---|
| `total` | Total findings checked. |
| `in_scope` | Count of `in-scope` findings. |
| `out_of_scope` | Count of `out-of-scope` findings. |
| `ambiguous` | Count of `ambiguous` findings. |

## Status values

The subagent may return any `worker-contract` status:

| Status | Meaning |
|---|---|
| `complete` | All findings were classified. |
| `partial` | Some findings were classified; an explanation is in `Blockers`. |
| `needs_input` | Required input was missing (e.g., no scope or no findings). |
| `blocked` | The scope is contradictory or otherwise unclassifiable. |

## Exit behavior

The subagent does not write files or change project state. It returns only the structured response.
