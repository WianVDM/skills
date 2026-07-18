# Shared configuration keys

**Layer:** proposed architecture. **Mode:** reference.

This registry defines the canonical shared keys that skills can declare in their `config.yaml` files. Shared keys are written to `.agents/config/shared.yaml` once per workspace and read by every skill that needs them.

## Registering a new key

Before adding a shared key to a skill's `config.yaml`, register it here with:

- A stable, lowercase, snake_case key name.
- A clear description of what it controls.
- A sensible default.
- The type or allowed values.

This prevents duplicate prompting and keeps shared semantics consistent across skills.

## Current keys

| Key | Type | Default | Description |
|---|---|---|---|
| `agents.context_dir` | string | `.agents/context` | Directory for cross-skill context reports. |
| `agents.config_dir` | string | `.agents/config` | Directory for skill configuration files. |
| `issue_tracker` | enum | `github` | Where the project tracks issues. Allowed values: `github`, `gitlab`, `linear`, `jira`, `local`, `other`. |

## Namespacing

Prefix skill-specific keys with the skill name to avoid collisions:

```yaml
skill:
  - key: debrief.default_tracker
    required: false
    default: ${issue_tracker}
```

Shared keys should be generic enough that multiple skills can read them.
