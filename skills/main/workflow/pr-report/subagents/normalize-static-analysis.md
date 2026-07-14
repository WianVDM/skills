# Normalize Static Analysis

Follow the `worker-contract` return contract. Normalizes raw static-analysis tool output into the internal `pr-report` normalization model.

## In scope

- Accept raw code-quality findings and severity mappings from a tool.
- Map the raw output to the normalized internal model.
- Set confidence based on mapping completeness and quality.
- Handle missing or partial fields gracefully.

## Inputs

- Capability name: `static_analysis`
- Raw tool output (e.g., from SonarCloud MCP, SonarCloud API, manual input)
- Tool name and provider name (e.g., `sonarcloud_mcp`, `sonarcloud_api`, `manual`)
- Optional mapping hints for non-standard providers

## Outputs

Return the standard worker contract with a `Findings` section containing the normalized envelope and findings:

### Envelope

```yaml
capability: static_analysis
status: complete | partial | missing | degraded
tool: string
source: string
confidence: high | medium | low
findings: []
errors: []
better_tool: string | null
```

### Normalized findings

- **Finding:** `rule`, `message`, `severity`, `path`, `line`, `effort`, `status`.

## Rules

- Map fields that exist; leave missing fields absent rather than inventing defaults.
- Normalize severity to the skill's internal scale when possible (blocker, required, recommended, informational).
- Set confidence to `high` only when all required fields are present and the mapping is direct.
- Set confidence to `medium` when severity mapping or line numbers require inference.
- Set confidence to `low` when rule or message text is missing or ambiguous.
- Record any degradation notes in `errors` (e.g., missing file paths, provider-specific severity names).
- Do not write to the report or state files.
- Escalate to `needs_input` if the raw output cannot be mapped at all.
