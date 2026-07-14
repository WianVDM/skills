# search-skills-registry

A model-invoked building block that searches configured skill registries for third-party skills.

## When to use

Use this skill when you need to:

- Find existing skills that might cover a problem.
- Compare third-party alternatives before creating a new skill.
- Discover skills from a custom registry.

## How to use

Invoke the skill by name, or run the script directly:

```bash
python scripts/search-skills-registry.py "lint typescript" --json
python scripts/search-skills-registry.py "lint typescript" --registry npm --json
```

## Using this skill from a conductor

A conductor should call the script, inspect the `results` array, and present alternatives to the user. If the user chooses to install a result, use the `install_command` field directly:

```bash
# From search-skills-registry output
{
  "install_command": "install-skill lint-ts --source https://example.com/lint-ts.zip"
}

# Conductor invokes:
python skills/install-skill/scripts/install-skill.py lint-ts --source https://example.com/lint-ts.zip --scope project --yes
```

Do not fabricate `--registry` or other flags not present in `install_command`. If the skill already exists, omit `--yes` until the user explicitly approves the overwrite.

## Configuration

Registries are configured in `.agents/config/write-a-skill.yaml`. See [`references/REGISTRY_CONFIGURATION.md`](references/REGISTRY_CONFIGURATION.md) for the full format, supported `source_type` values, and built-in defaults.

If no configuration is found, the script uses a minimal built-in default set.

## Output

The skill returns a structured report with:

- `query`: the original search query.
- `registries`: list of registry names searched.
- `results`: normalized list of candidate skills.
- `errors`: list of registry errors encountered.

Each result includes `source`, `name`, `description`, `trust_signals`, and `install_command`.

## Directory layout

```
search-skills-registry/
├── SKILL.md
├── README.md
├── references/
│   └── REGISTRY_CONFIGURATION.md
└── scripts/
    └── search-skills-registry.py
```

## Key conventions

- **Search only:** never installs.
- **Graceful degradation:** unavailable registries are reported as errors but do not fail the whole search.
- **Trust signals:** reports available signals; does not make trust judgments.
- **No user interaction:** the caller decides what to install.

## Maintenance notes

- Frontmatter parsing is delegated to the shared `parse-skill-frontmatter` skill.
- Add new `source_type` handlers by extending the script.
- Keep default registries conservative and well-known.
- Update the install command format if `install-skill` changes its interface.
