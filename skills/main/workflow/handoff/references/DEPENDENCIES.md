# Dependencies

## Required binaries

- Python 3.10 or later

## Required tools

- Filesystem read/write access to the project context directory and config directory.
- YAML support is preferred for config files. If PyYAML is unavailable, the helper falls back to JSON and discloses the degraded source.

## Required skills

- None.

## Recommended skills

- `detect-project-context` — if available, the agent may use it to locate the project context and config directories. The helper falls back to its own detection when the skill is not available.
- `context-reports` — the handoff output follows the shared context-report conventions (frontmatter envelope, canonical location, freshness expectations). The skill does not require it at runtime.

## Optional skills

- None.

## Required MCP servers

- None.

## Environment variables

- None.

## Consumed reports

- None.

## Produced reports

- `{context_dir}/handoff/{key}.md` — the latest handoff for a key.
- `{context_dir}/handoff/{key}-{timestamp}-archive.md` — archived previous handoff, when archiving is enabled.

## Configuration files

- `.agents/config/shared.yaml` — shared workspace keys (`agents.context_dir`, `agents.config_dir`).
- `.agents/config/handoff.yaml` — skill-specific keys (`handoff.default_level`, `handoff.archive_old`, `handoff.include_chain`).
