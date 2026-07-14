# Normalize CI

Follow the `worker-contract` return contract. Normalizes raw CI / build tool output into the internal `pr-report` normalization model.

## In scope

- Accept raw check runs, conclusions, required checks, and failing-log summaries from a tool.
- Map the raw output to the normalized internal model.
- Set confidence based on mapping completeness and quality.
- Handle missing or partial fields gracefully.

## Inputs

- Capability name: `ci_build`
- Raw tool output (e.g., from GitHub MCP, `gh` CLI, manual input)
- Tool name and provider name (e.g., `github_mcp`, `gh_cli`, `manual`)
- Optional mapping hints for non-standard providers

## Outputs

Return the standard worker contract with a `Findings` section containing the normalized envelope and findings:

### Envelope

```yaml
capability: ci_build
status: complete | partial | missing | degraded
tool: string
source: string
confidence: high | medium | low
findings: []
errors: []
better_tool: string | null
```

### Normalized findings

- **Check / build:** `name`, `conclusion` (success/failure/skipped/neutral/pending), `required`, `url`, `log_summary`.

## Rules

- Map fields that exist; leave missing fields absent rather than inventing defaults.
- Set confidence to `high` only when all required fields are present and the mapping is direct.
- Set confidence to `medium` when log summaries or required-flag data is missing.
- Set confidence to `low` when check conclusions are missing or ambiguous.
- Record any degradation notes in `errors` (e.g., missing log summaries, partial check lists).
- Do not write to the report or state files.
- Escalate to `needs_input` if the raw output cannot be mapped at all.
