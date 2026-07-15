# Config format for consuming skills

`initialize-skill` reads a skill's `config.yaml` to extract defaults and expected types. The file must be YAML and lives next to the skill's `SKILL.md`.

## Top-level keys

```yaml
shared:
  - key: agents.context_dir
    required: true
    default: .agents/context
    description: Project context directory.

skill:
  - key: debrief.green_threshold
    required: true
    default: 85
    description: Integer threshold for Green confidence.

requires_setup: true
```

### `shared`

A list of keys that are normally resolved by `detect-project-context` and stored in `{config_dir}/shared.yaml`. `initialize-skill` does not write `shared.yaml`, but it will read it if present and merge it under the skill-specific config.

### `skill`

A list of keys that belong to this skill. `initialize-skill` extracts `key` and `default` to build the proposed project config.

Each item supports:

| Field | Required | Description |
|---|---|---|
| `key` | yes | The config key. Can be a flat key or a dot-prefixed nested key (e.g., `pr-report.tools.pr.provider`). |
| `required` | no | Whether the key must be present. Defaults to false. |
| `default` | no | The default value used when the key is missing. |
| `description` | no | Human-readable description shown in proposals. |

### `requires_setup`

A boolean indicating whether the skill requires first-run initialization. If true, the conductor should invoke `initialize-skill` before running the main workflow.

## Key naming

Keys can be flat:

```yaml
skill:
  - key: green_threshold
    default: 85
```

Or nested with a skill prefix:

```yaml
skill:
  - key: pr-report.tools.pr.provider
    default: auto
```

When a skill prefix is present, `initialize-skill` strips the prefix when writing the project config. For example, `pr-report.tools.pr.provider` becomes `tools.pr.provider` in `{config_dir}/pr-report.yaml`.

## Type handling

`load-skill-config.py` type-checks the merged config against the defaults. The expected type is inferred from the default value:

- `bool` default → boolean expected.
- `int` default → integer expected.
- `str` default → string expected.
- `list` default → list expected.
- `dict` default → mapping expected; nested dicts are checked recursively.

Type mismatches are reported as errors but do not prevent the config from being returned.

## Example

```yaml
# config.yaml for a fictional skill named my-skill
shared:
  - key: agents.config_dir
    required: true
    default: .agents/config

skill:
  - key: my-skill.timeout_seconds
    required: true
    default: 30
    description: Timeout for external tool calls.

  - key: my-skill.tools.pr.provider
    required: true
    default: auto
    description: Preferred PR provider.

  - key: my-skill.features.advanced
    required: false
    default: false
    description: Enable advanced features.

requires_setup: true
```

The proposed project config would be:

```yaml
timeout_seconds: 30
tools:
  pr:
    provider: auto
features:
  advanced: false
schema_version: "1.0.0"
```
