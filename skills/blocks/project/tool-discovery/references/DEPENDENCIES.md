# Dependencies

## Required

- **Python 3.10+** — scripts are written in Python 3.
- **PyYAML** — required for parsing the capability registry and config files.

## Required skills

None. The block takes explicit paths and capability names as input.

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
