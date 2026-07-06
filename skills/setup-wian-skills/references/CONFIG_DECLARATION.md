# Config declaration format

Skills declare their configuration requirements in a `config.yaml` file next to `SKILL.md`.

## Example

```yaml
shared:
  - key: agents.context_dir
    required: true
    default: .agents/context
  - key: issue_tracker
    required: true
    default: github

skill:
  - key: debrief.default_tracker
    required: false
    default: ${issue_tracker}

requires_setup: true
```

## Fields

- `shared`: keys that are written to `.agents/config/shared.yaml` and shared across skills.
- `skill`: keys that are written to `.agents/config/{skill-name}.yaml` and are private to the skill.
- `requires_setup`: when `true`, the skill appears in the initialization checklist after sync.

Shared keys must be defined in the central registry at `docs/skill-standards/CONFIG_KEYS.md`. Unregistered keys are treated as skill-specific.
