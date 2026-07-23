---
name: tool-discovery
description: Discover and rank available tools for a given capability, resolve them into validated per-project recipes, and cache those recipes for reuse. Given a capability like pr-source or ci-source, returns ranked tools with confidence, platform detection, and a recipe cache that survives across runs.
invocation: model-invoked
---

# tool-discovery

## Purpose

Given a capability (e.g., `pr-source`, `ci-source`, `issue-tracker-source`), find the best working tool for it in the current environment, resolve that tool into a concrete recipe (exact calls, arguments, field mappings), validate the recipe against the contract it must fill, and cache it per project so derivation happens once.

## Skill type

Building block. It discovers, resolves, and caches tools; it does not invoke them on the conductor's behalf or store their output.

## When to use

A conductor skill needs to know which tool to use for a capability before it calls the tool. Use `tool-discovery` when:

- The best tool depends on the project environment.
- Multiple tools might satisfy the same capability.
- The skill wants its tool-selection logic visible and recorded.
- A previously derived recipe may be reusable (cache hit) or stale (re-derive).

## In scope

- Model-first detection: in-session MCP/harness tools, platform detection from the git origin remote, CLI probes with auth checks.
- Script-based detection as the offline fallback: `scripts/discover-tools.py` searches known MCP config locations, probes CLIs, detects platform, and ranks tools.
- Capability resolution: deriving a concrete recipe per [references/RESOLUTION_GUIDE.md](references/RESOLUTION_GUIDE.md).
- The per-project recipe cache (`{config_dir}/tool-recipes.yaml`): read, write, invalidate via script operations.
- Ranking discovered tools by confidence and configured preference.

## Out of scope

- Invoking the discovered tools or their recipes (conductors do that).
- Resolving tokens (delegate to `token-resolver`).
- Storing tool *output* as observations (consumers do that via `chainlog`).
- Deciding whether cached results are fresh (use `artifact-freshness` if caching output; the recipe cache re-validates via its own probe).

## Core contract

Accepts a capability name and project context. Returns a ranked list of tools with category, availability, confidence, auth state, and the detected platform. Separately, manages the per-project recipe cache.

## Detection order

1. **Model-first (preferred).** The running model sees connected MCP and harness tools directly. Follow [references/RESOLUTION_GUIDE.md](references/RESOLUTION_GUIDE.md): name the capability, enumerate session tools, detect platform from `git remote get-url origin`, probe CLI presence and auth, derive and validate the recipe.
2. **Script fallback.** `scripts/discover-tools.py` for script-only contexts. It searches the config dir, the project root, and known harness MCP config locations (`~/.pi/agent/mcp.json`, `~/.claude.json`, `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`, and others), probes CLI auth when asked, and detects the platform from the origin remote. Its output is a floor, not a ceiling — it cannot see session-only tools.

## Operations

- `discover` — return ranked tools for a capability, plus the detected platform.
- `cache-get` — read the cached recipe for a capability (`found` / `not_found`).
- `cache-put` — write or update the cached recipe for a capability.
- `cache-invalidate` — remove the cached recipe for a capability.

## Input

JSON on stdin:

```json
{
  "operation": "discover",
  "capability": "pr-source",
  "config_dir": ".agents/config",
  "project_root": ".",
  "preference": "auto",
  "probe": true,
  "search_scope": "all"
}
```

| Field | Default | Meaning |
|---|---|---|
| `probe` | `false` | Run auth probes (`gh auth status`, `glab auth status`) for detected CLIs. |
| `search_scope` | `all` | `all` searches home + project locations; `project` restricts to the project (used by tests and sandboxed runs). |

## Output

JSON on stdout:

```json
{
  "status": "found",
  "capability": "pr-source",
  "platform": "github",
  "tools": [
    {"name": "github-mcp", "category": "mcp", "available": true, "confidence": "high", "detail": "MCP keywords github matched"},
    {"name": "gh-cli", "category": "cli", "available": true, "confidence": "high", "detail": "binary gh found on PATH; authenticated", "auth": "authenticated"},
    {"name": "manual", "category": "manual", "available": true, "confidence": "low", "detail": "user-provided fallback"}
  ]
}
```

See [references/INTERFACE.md](references/INTERFACE.md) for the full schema, cache operation payloads, and [references/CAPABILITY_REGISTRY.md](references/CAPABILITY_REGISTRY.md) for the bundled capability definitions.

## Recipe cache

Validated recipes live in `{config_dir}/tool-recipes.yaml`, one entry per capability. The format, derivation flow, validation rules, and invalidation triggers are defined in [references/RESOLUTION_GUIDE.md](references/RESOLUTION_GUIDE.md). A cached recipe is reused until its `revalidate` probe fails, the tool disappears, or the user resets it.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Resolution guide](references/RESOLUTION_GUIDE.md) — model-first detection, concept mappings, provider quirks, recipe cache format.
- [Interface](references/INTERFACE.md)
- [Capability Registry](references/CAPABILITY_REGISTRY.md)
- [Dependencies](references/DEPENDENCIES.md)
