---
name: pr-report-adapter-architecture
description: High-level adapter architecture for the redesigned pr-report skill. Defines the adapter taxonomy, discovery model, and conductor responsibilities without duplicating the detailed interface contract.
metadata:
  author: Wian van der Merwe
  tags: [pr-report, architecture, adapters, pluggability]
  version: "1.0.0"
---

# PR Report Adapter Architecture

`pr-report` is a thin conductor. It consumes normalized output from the best available tool for each capability and owns synthesis, triage, and reporting. Adapters translate provider-specific data into the normalized shapes defined by the `pr-adapter-contract` building block.

Adapters are one implementation strategy, not the only source of truth. The conductor also considers MCP tools, native binaries, direct APIs, and manual fallback. The full capability-to-tool mapping is in [TOOL_SELECTION.md](TOOL_SELECTION.md).

## Adapter taxonomy

| Role | Provides | Examples |
|---|---|---|
| `pr-source` | PR metadata, changed files, reviews, inline threads | GitHub, GitLab, Gitea, Azure DevOps, Bitbucket, Manual |
| `ci-source` | Check/pipeline status and failing logs | GitHub Actions, Azure Pipelines, GitLab CI, Jenkins |
| `static-analysis-source` | Code-quality findings | SonarQube, SonarCloud, CodeQL, Semgrep, Codacy |
| `issue-tracker-source` | Ticket scope, acceptance criteria | Jira, Linear, GitHub Issues, Azure Boards |
| `notification-source` | Feedback from chat/email/meeting tools | Teams, Slack, email, meeting notes |
| `context-report-source` | Pre-existing `.agents/context/` reports | Any skill report |

## Interface contract

The full contract — envelope shape, status semantics, operation schemas, and adapter rules — lives in the `pr-adapter-contract` building block. Adapters and the conductor both reference it as the single source of truth.

## Discovery and registration

Adapters are one source among skill adapters, MCP tools/servers, native binaries, direct APIs, and manual fallback. The conductor selects the best tool for each capability using the rules in [TOOL_SELECTION.md](TOOL_SELECTION.md).

Adapters may be registered by name in `pr-report` config. The conductor does not hardcode adapter names, but it does ship with a default registry. Users can override or extend the registry per project. See [ADAPTER_REGISTRY.md](ADAPTER_REGISTRY.md) for the registry and [CONFIG_PATTERN.md](CONFIG_PATTERN.md) for config schema.

### Discovery rules

1. Discover all available tool categories first (adapters, MCP tools, native binaries, direct APIs) using [TOOL_SELECTION.md](TOOL_SELECTION.md).
2. If a configured adapter is the best available tool for a capability, invoke it.
3. If the configured adapter is not the best available tool, disclose the better tool and ask the user whether to switch.
4. If `source` is `auto`, detect from the PR source, environment variables, MCP config, or config files.
5. If `source` is a file path, treat it as a script or config-only adapter.
6. If `source` is `manual` or missing, use the manual adapter.

## Built-in adapters

The redesigned `pr-report` ships with a small set of built-in adapters. See [ADAPTER_REGISTRY.md](ADAPTER_REGISTRY.md) for the full catalog and status.

## Manual adapter

The manual adapter is the default for unsupported tools and manual processes. It is a first-class adapter, not a degraded fallback. It is used when it is the best or only available tool for a capability. Details, input modes, and formats live in `manual-pr-adapter`.

## Config-only adapter

For internal or custom tools, a user can write a YAML adapter definition that a generic `http-adapter` or `csv-adapter` building block interprets. The shape is documented in the `pr-adapter-contract` building block.

## Context-report consumption

Any tool or process can write a context report to `.agents/context/` and the `context-report-adapter` will consume it. The report format is defined by the `context-reports` building block.

## Token resolution

Adapters do not resolve their own tokens. The shared `token-resolver` building block resolves tokens and passes them to adapters via config. Adapters never log tokens.

## Error handling

Adapters must distinguish five states: `complete`, `partial`, `needs_input`, `blocked`, and `skipped`. The conductor handles each as follows:

| Status | Conductor behavior |
|---|---|
| `complete` | Use the data. |
| `partial` | Check whether a better tool is available; if so, fall back to it before accepting the partial data. If the best available tool is still partial, disclose and apply `tooling.degraded_mode`. |
| `needs_input` | Ask the user and retry. |
| `blocked` | Stop and consult the user. |
| `skipped` | Continue without that source. |

If a better tool is available for a capability but the configured adapter returned `partial` or `blocked`, the conductor must disclose the better tool and offer to switch before accepting degradation.

## Adapter checklist

Before adding a new adapter, verify it:

- Implements the correct `pr-adapter-contract` interface.
- Returns the normalized shape, not raw provider data.
- Does not hardcode tokens or project-specific paths.
- Handles errors and returns the correct status.
- Is registered in the adapter registry or config.
- Declares its own dependencies.

## Out of scope

Adapters do not synthesize or triage issues, write the PR report, fix code, or reply to comments. They only bridge provider-specific data into the normalized shape.

## References

- `pr-adapter-contract` — normalized adapter interface
- `token-resolver` — token resolution
- `context-reports` — context report format
- `manual-pr-adapter` — manual adapter details
- [TOOL_SELECTION.md](TOOL_SELECTION.md) — capability-to-tool mapping and selection rules
- [ADAPTER_REGISTRY.md](ADAPTER_REGISTRY.md) — default adapter registry
- [CONFIG_PATTERN.md](CONFIG_PATTERN.md) — adapter config
- [COMMENT_TRIAGE.md](COMMENT_TRIAGE.md) — how normalized items are triaged
- [CHECKPOINTING.md](CHECKPOINTING.md) — state and resumption
- `worker-contract` skill — worker return format
