# Config format for consuming skills

`initialize-skill` reads a skill's `config.yaml` to extract defaults, required keys, and expected types. The file is YAML and lives next to the skill's `SKILL.md`. The formal schema is `docs/skill-standards/schemas/config-yaml.schema.json`.

## Top-level keys

```yaml
shared:
  - key: agents.context_dir
    required: true
    default: .agents/context
    type: string
    description: Project context directory.

skill:
  - key: my-skill.timeout_seconds
    required: true
    default: 30
    type: integer
    description: Timeout for external calls.

requires_setup: true
```

### `shared`

Keys resolved by `detect-project-context` and stored in `{config_dir}/shared.yaml`. `initialize-skill` reads `shared.yaml` for the effective view but never writes it, and never copies shared keys into `{skill}.yaml`.

Shared keys must be registered in `docs/skill-standards/reference/config-keys.md`. Unregistered keys are treated as skill-specific.

### `skill`

Keys that belong to this skill and live in `{config_dir}/{skill}.yaml`. Each item supports:

| Field | Required | Description |
|---|---|---|
| `key` | yes | Flat key (`timeout`) or nested key with the skill-name prefix (`my-skill.tools.pr.provider`). |
| `required` | no | Whether the skill cannot function without a value. Defaults to false. |
| `default` | no | Value used when the key is missing in every layer. |
| `type` | no | Expected value type (`string`, `boolean`, `integer`, `array`, `object`). |
| `description` | no | Human-readable explanation shown in proposals. |

### `requires_setup`

Boolean. If true, a setup conductor should run initialization before the skill's main workflow.

## Key naming

Nested keys must carry the skill-name prefix, which is stripped when writing:

```yaml
- key: my-skill.tools.pr.provider   # becomes tools.pr.provider in my-skill.yaml
  default: auto
```

A dotted key whose first segment is not the skill name is rejected with an error. Flat keys are used as-is.

## Type handling

`load-skill-config.py` type-checks the merged config against the defaults; the expected type is inferred from the default value. Nested dicts are checked recursively; `bool` is checked before `int`. Mismatches are reported but never block the config from being returned.

## Example

The declaration above (`my-skill.timeout_seconds` etc.) produces this proposed project config:

```yaml
timeout_seconds: 30
schema_version: "1.0.0"
```
