# Normalize PR

Follow the `worker-contract` return contract. Normalizes raw PR source tool output into the internal `pr-report` normalization model.

## In scope

- Accept raw PR metadata, changed files, top-level reviews, and inline review threads from a tool.
- Map the raw output to the normalized internal model.
- Set confidence based on mapping completeness and quality.
- Handle missing or partial fields gracefully.

## Inputs

- Capability name: `pr_metadata`, `changed_files`, `reviews`, or `threads`
- Raw tool output (e.g., from GitHub MCP, `gh` CLI, manual input)
- Tool name and provider name (e.g., `github_mcp`, `gh_cli`, `manual`)
- Optional mapping hints for non-standard providers

## Outputs

Return the standard worker contract with a `Findings` section containing the normalized envelope and findings:

### Envelope

```yaml
capability: pr_metadata | changed_files | reviews | threads
status: complete | partial | missing | degraded
tool: string
source: string
confidence: high | medium | low
findings: []
errors: []
better_tool: string | null
```

### Normalized findings

- **PR metadata:** `title`, `body`, `author`, `state`, `url`, `base_branch`, `head_branch`, `draft`, `created_at`, `updated_at`.
- **Changed files:** `path`, `status` (added/removed/modified), `patch` (optional), `previous_path`.
- **Reviews:** `id`, `author`, `body`, `state` (APPROVED/CHANGES_REQUESTED/COMMENTED), `submitted_at`.
- **Threads / comments:** `id`, `thread_id`, `author`, `body`, `path`, `line`, `created_at`, `status`.

## Rules

- Map fields that exist; leave missing fields absent rather than inventing defaults.
- Set confidence to `high` only when all required fields are present and the mapping is direct.
- Set confidence to `medium` when one or more optional fields are missing or the mapping requires light inference.
- Set confidence to `low` when required fields are missing or the mapping is ambiguous.
- Record any degradation notes in `errors` (e.g., partial review bodies, missing line numbers).
- Do not write to the report or state files.
- Escalate to `needs_input` if the raw output cannot be mapped at all.
