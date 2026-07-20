# Config declaration format

Skills declare their configuration requirements in a `config.yaml` file next to `SKILL.md`. The canonical schema for this format is `config-yaml.schema.json` in the skill-standards schemas directory.

## Example

```yaml
shared:
  - key: agents.context_dir
    required: true
    default: .agents/context  # actual value resolved per workspace by detect-project-context
  - key: issue_tracker
    required: true
    default: github
  - key: debrief.default_tracker
    required: false
    default: ${issue_tracker}

skill:
  - key: debrief.private_token
    required: false

requires_setup: true
```

The default value `.agents/context` is the conventional default for the `agents.context_dir` key. The actual directory is resolved by `setup-wian-skills` using `detect-project-context` before writing the shared config.

## Fields

- `shared`: keys that are written to `{config_dir}/shared.yaml` and shared across skills, where `{config_dir}` is the recommended config directory from `detect-project-context`.
- `skill`: keys that are written to `{config_dir}/{skill-name}.yaml` and are private to the skill.
- `requires_setup`: when `true`, the skill appears in the initialization checklist after setup.

A `skill` key may declare `bootstrap: true` to opt out of lazy loading. Bootstrap keys always resolve during setup, even in the **lazy** branch. Use it for private keys a skill cannot function without on its very first run.

Shared keys should be registered in the project's central config key registry. The setup skill does not read the registry; it treats unregistered keys as skill-specific.

## Key deduplication and inference

When multiple skills declare the same `shared` key, the setup skill asks for the value once and writes it once. The key is associated with every skill that consumes it.

A default value may reference another key using `${other_key}` syntax. If `other_key` has already been resolved (from an existing shared config file or an earlier answer), the default is filled in automatically. If not, the referenced key is resolved first.

## Dynamic questionnaire

The setup skill gathers all configuration keys before asking questions. While the user is asked one question at a time, each answer can affect later questions:

- A later key may be skipped because its value can be inferred from an earlier answer.
- A later question's wording or options may change based on an earlier answer.
- A later key may become required only when an earlier answer has a specific value.

To support this, a key may declare a `depends_on` field:

```yaml
shared:
  - key: issue_tracker
    required: true
    default: github
  - key: jira.project_key
    required: false
    default: null
    depends_on:
      key: issue_tracker
      value: jira
```

In this example, `jira.project_key` is only asked when `issue_tracker` is `jira`.

## Required key handling

If a key is `required: true` and has no `default` and the user provides no answer, the setup skill stops and explains what is missing. It does not continue with a partial configuration.

## Lazy loading policy

Bundle skills are assumed to follow the lazy-loading pattern: private configuration resolves on first use through the skill's own `## Initialization` section (which invokes `initialize-skill`), not at setup time.

The setup skill applies this policy per key:

- `shared` keys always resolve at setup, in every branch. They are the bindings to the global shared config, and nothing in the first-use path is allowed to write `shared.yaml`.
- `skill` keys defer to first use in the **lazy** branch, but only when the owning skill is lazy-eligible — its `SKILL.md` contains an `## Initialization` section. A skill without that section is not lazy-eligible, and its keys resolve at setup in every branch.
- `skill` keys with `bootstrap: true` resolve at setup in every branch.
- In the **full** branch, every key resolves at setup regardless of eligibility.
