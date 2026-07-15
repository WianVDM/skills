# Dependencies

## Required

- **Python 3.10+** — scripts are written in Python 3.
- **PyYAML** — required for YAML parsing and writing.

## Required skills

- `detect-project-context` — provides the `marker_dir` and config directory location.
- `worker-contract` — return contract used if the block is invoked through a subagent.
- `context-reports` — context report conventions if the block writes state.

## Recommended

None.

## Optional

None.

## Binaries

None beyond Python and PyYAML.

## Consumed references

- `{skill_dir}/config.yaml` — loaded by `initialize.py` to extract defaults.
- `{marker_dir}/config/shared.yaml` — loaded by both scripts.
- `{marker_dir}/config/{skill}.yaml` — loaded and optionally written by `initialize.py`.

## Produced artifacts

- `{marker_dir}/config/{skill}.yaml` — the project-level config for the consuming skill.
- `{marker_dir}/config/{skill}.yaml.backup.{timestamp}` — backup of an existing config before overwriting.
