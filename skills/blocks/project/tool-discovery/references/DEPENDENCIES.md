# Dependencies

## Required

- **Python 3.10+** — scripts are written in Python 3.
- **PyYAML** — required for parsing the capability registry and config files.

## Required skills

- `worker-contract` — return contract used if the block is invoked through a subagent.
- `context-reports` — conventions for context directory layout and report schemas.
- `initialize-skill` — load project config and defaults.
- `token-resolver` — resolve secure tokens when needed by consumers.

## Recommended

- `artifact-freshness` — if the consumer caches discovery results.

## Optional

None.

## Binaries

None beyond Python and PyYAML. The block checks for other binaries but does not require them.

## Consumed references

- `{skill_dir}/scripts/capability-registry.yaml` — bundled registry of known tools.
- `{config_dir}/tool-discovery.yaml` — optional project-level preferences.
- `{config_dir}/mcp.json` / `{config_dir}/mcp.yaml` — MCP server configuration.

## Produced artifacts

None. This block is read-only.
