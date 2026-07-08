---
name: pr-report-adapter-architecture
description: High-level adapter architecture for the redesigned pr-report skill. Defines the adapter taxonomy, discovery model, and conductor responsibilities without duplicating the detailed interface contract.
metadata:
  author: Wian van der Merwe
  tags: [pr-report, architecture, adapters, pluggability]
  version: "1.0.0"
---

# PR Report Adapter Architecture

`pr-report` is a thin conductor. It consumes normalized adapter output and owns synthesis, triage, and reporting. Adapters translate provider-specific data into the normalized shapes defined by the `pr-adapter-contract` building block.

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

Adapters are registered by name in `pr-report` config. The conductor does not hardcode adapter names. The default registry ships with the conductor; users can override or extend it per project. See [ADAPTER_REGISTRY.md](ADAPTER_REGISTRY.md) for the registry and [CONFIG_PATTERN.md](CONFIG_PATTERN.md) for config schema.

### Discovery rules

1. If `source` is a known adapter name, invoke it.
2. If `source` is `auto`, detect from the PR source, environment variables, or config files.
3. If `source` is a file path, treat it as a script or config-only adapter.
4. If `source` is `manual` or missing, use the manual adapter.

## Built-in adapters

The redesigned `pr-report` ships with a small set of built-in adapters. See [ADAPTER_REGISTRY.md](ADAPTER_REGISTRY.md) for the full catalog and status.

## Manual adapter

The manual adapter is the default for unsupported tools and manual processes. It is a first-class adapter, not a degraded fallback. Details, input modes, and formats live in `manual-pr-adapter`.

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
| `partial` | Use what is available and note gaps. |
| `needs_input` | Ask the user and retry. |
| `blocked` | Stop and consult the user. |
| `skipped` | Continue without that source. |

The conductor does not fail because one adapter is missing. It reports plainly which sources are unavailable and proceeds with the rest.

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
- [ADAPTER_REGISTRY.md](ADAPTER_REGISTRY.md) — adapter registry
- [CONFIG_PATTERN.md](CONFIG_PATTERN.md) — adapter config
- [COMMENT_TRIAGE.md](COMMENT_TRIAGE.md) — how normalized items are triaged
- [CHECKPOINTING.md](CHECKPOINTING.md) — state and resumption
- `worker-contract` skill — worker return format
