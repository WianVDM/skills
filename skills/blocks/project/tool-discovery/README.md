# tool-discovery

Discover and rank available tools for a given capability.

## What it does

`tool-discovery` tells a conductor which tools are available for a capability such as `pr-source`, `ci-source`, `issue-tracker-source`, or `static-analysis-source`. It returns a ranked list so the conductor can choose the best tool and disclose its fallbacks.

## Directory layout

```text
tool-discovery/
├── SKILL.md
├── README.md
├── config.yaml
├── scripts/
│   └── discover-tools.py
├── references/
│   ├── INTERFACE.md
│   ├── DEPENDENCIES.md
│   └── CAPABILITY_REGISTRY.md
└── evals/
    └── evals.json
```

## Key conventions

- Capabilities are strings like `pr-source`, `ci-source`, `issue-tracker-source`.
- Tool categories are `mcp`, `cli`, `api`, `harness`, `manual`.
- The manual fallback is always reported as available with low confidence.
- User preferences in config override the default ranking.
- The block does not invoke tools; it only reports what is available.

## When to maintain or extend this block

- Add a new capability to the registry.
- Add new known tools for an existing capability.
- Change the ranking algorithm or confidence rules.

## Shared building blocks

- `initialize-skill` — load project config and preferences.
- `token-resolver` — resolve tokens for API or MCP tools.
- `worker-contract` — return format if invoked through a subagent.
- `context-reports` — conventions for context directory layout.

## How to update

- Keep the capability registry in `references/CAPABILITY_REGISTRY.md` and the bundled YAML registry up to date.
- Preserve backward compatibility for existing capability names.
- Bump the skill version when the interface or ranking changes.
