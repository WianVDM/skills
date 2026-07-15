---
name: tool-discovery
description: Discover and rank available tools for a given capability. Given a capability like pr-source or ci-source, returns a ranked list of available tools with confidence, source category, and fallback ordering.
version: 1.0.0
invocation: model-invoked
depends:
  - worker-contract
  - context-reports
  - initialize-skill
  - token-resolver
---

# tool-discovery

## Purpose

Given a capability (e.g., `pr-source`, `ci-source`, `issue-tracker-source`), discover the available tools and return them in ranked order so a conductor can pick the best one and fall back transparently.

## Skill type

Building block. It only discovers tools; it does not invoke them or store their output.

## When to use

A conductor skill needs to know which tool to use for a capability before it calls the tool. Use `tool-discovery` when:

- The best tool depends on the project environment.
- Multiple tools might satisfy the same capability.
- The skill wants to expose its tool-selection logic to the user.

## In scope

- Discover MCP tools, native binaries, direct API endpoints, harness tools, and manual fallback for a capability.
- Rank discovered tools by confidence and configured preference.
- Return a deterministic, reproducible ranking.

## Out of scope

- Invoking the discovered tools.
- Resolving tokens (delegate to `token-resolver`).
- Storing tool output as evidence (consumers do that via `evidence-store`).
- Deciding whether cached results are fresh (use `artifact-freshness` if caching).

## Core contract

Accepts a capability name and project context. Returns a ranked list of tools with their category, availability, confidence, and source detail.

## Operations

- `discover` — return ranked tools for a capability.

## Input

JSON on stdin:

```json
{
  "operation": "discover",
  "capability": "pr-source",
  "context_dir": ".agents/context",
  "config_dir": ".agents/config",
  "preference": "auto"
}
```

## Output

JSON on stdout:

```json
{
  "status": "found",
  "capability": "pr-source",
  "tools": [
    {
      "name": "github-mcp",
      "category": "mcp",
      "available": true,
      "confidence": "high",
      "detail": "MCP tools github_get_pull_request and github_get_pull_request_reviews available"
    },
    {
      "name": "gh-cli",
      "category": "cli",
      "available": true,
      "confidence": "medium",
      "detail": "gh binary found on PATH"
    },
    {
      "name": "manual",
      "category": "manual",
      "available": true,
      "confidence": "low",
      "detail": "user-provided fallback"
    }
  ]
}
```

See [references/INTERFACE.md](references/INTERFACE.md) for the full schema and [references/CAPABILITY_REGISTRY.md](references/CAPABILITY_REGISTRY.md) for the bundled capability definitions.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Interface](references/INTERFACE.md)
- [Capability Registry](references/CAPABILITY_REGISTRY.md)
- [Dependencies](references/DEPENDENCIES.md)
