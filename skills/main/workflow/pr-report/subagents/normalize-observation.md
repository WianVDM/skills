# Normalize Observation

Follow the `worker-contract` return contract. Normalizes raw tool output for one capability into the [`pr-adapter-contract`](../../../../blocks/project/pr-adapter-contract/SKILL.md) normalized shape for that capability's adapter role.

## In scope

- Accept raw tool output for a single capability: `pr_metadata`, `changed_files`, `reviews`, `threads`, `conversation_comments`, `ci_build`, `static_analysis`, or `issue_tracker_scope`.
- Map the raw output to the `pr-adapter-contract` shape for the matching role (`pr-source`, `ci-source`, `static-analysis-source`, `issue-tracker-source`).
- Set confidence based on mapping completeness and quality.
- Handle missing or partial fields gracefully.

## Out of scope

- Fetching data from tools. The conductor collects; this worker only normalizes.
- Writing to report or state files.
- Triage, synthesis, or scope decisions.

## Inputs

- Capability name and its adapter role.
- Raw tool output (from an MCP server, CLI, direct API, or manual input).
- Tool name and provider name (e.g., `github_mcp`, `gh_cli`, `sonarcloud_api`, `manual`).
- Optional mapping hints for non-standard providers.

## Outputs

Return the standard worker contract with a `Findings` section containing the normalized envelope and findings.

### Envelope

```yaml
capability: string         # e.g., pr_metadata, ci_build, static_analysis
status: complete | partial | needs_input | blocked | skipped   # pr-adapter-contract statuses
tool: string               # pr-report extension: the tool that produced the data
source_type: string        # provider name, e.g., github, sonarcloud, jira
confidence: high | medium | low
findings: []
errors: []                 # degradation notes, including inconclusive-result warnings
better_tool: string | null # pr-report extension: better tool available but unused
```

### Normalized findings

Use the `pr-adapter-contract` operation shapes for the capability's role:

| Capability | Contract operation | Fields |
|---|---|---|
| `pr_metadata` | `fetch_metadata` | `title`, `body`, `author`, `state`, `url`, `base_branch`, `head_branch`, `draft`, `created_at`, `updated_at` |
| `changed_files` | `fetch_changed_files` | `path`, `status`, `additions`, `deletions`, `previous_path` |
| `reviews` | `fetch_reviews` | `id`, `reviewer`, `state`, `body`, `submitted_at` |
| `threads` | `fetch_review_threads` | `id`, `thread_id`, `author`, `body`, `path`, `line`, `created_at`, `is_resolved` |
| `conversation_comments` | `fetch_feedback` | `id`, `author`, `body`, `created_at`, `source_type`, `channel`, `url` |
| `ci_build` | `fetch_check_runs` | `name`, `status`, `conclusion`, `url`, `is_required`, `summary` |
| `static_analysis` | `fetch_findings` | `key`, `rule`, `severity`, `message`, `path`, `line`, `status`, `url` |
| `issue_tracker_scope` | `fetch_scope` | `key`, `title`, `body`, `acceptance_criteria`, `status`, `url` |

## Rules

- Map fields that exist; leave missing fields absent rather than inventing defaults.
- Set confidence to `high` only when all required fields are present and the mapping is direct; `medium` for light inference; `low` when the mapping is ambiguous.
- An empty or unverifiable result (silently empty response, unconfirmed analysis existence) is **inconclusive**: return `partial` with `low` confidence and an `errors` note explaining why. Never return `complete` with empty findings for an inconclusive result.
- Record any degradation notes in `errors` (e.g., partial bodies, missing line numbers, provider-specific severity names).
- Normalize provider severities to the project's configured scale when possible; keep the raw value in `errors` when the mapping is uncertain.
- Do not write to the report or state files.
- Escalate to `needs_input` if the raw output cannot be mapped at all.
