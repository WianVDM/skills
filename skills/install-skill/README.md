# install-skill

A model-invoked building block that installs a skill from a local path or archive URL into the project or user scope.

## When to use

Use this skill when you need to:

- Install a skill from a local directory.
- Install a skill from a published archive URL.
- Confirm before overwriting an existing skill.

## How to use

Invoke the skill by name, or run the script directly:

```bash
# Install from a local directory
python scripts/install-skill.py example-skill --source /path/to/example-skill --scope project --yes

# Install from an archive URL
python scripts/install-skill.py example-skill --source https://example.com/example-skill.zip --scope project --yes
```

Use `--yes` to skip the interactive confirmation. Without `--yes`, the script prints the planned action and exits with code 1, letting the caller confirm.

## Output

The script returns a structured report:

- `installed`: `true` or `false`.
- `skill_name`: installed skill name.
- `target_scope`: `project` or `user`.
- `installed_path`: path where the skill was installed.

## Directory layout

```
install-skill/
├── SKILL.md
├── README.md
└── scripts/
    └── install-skill.py
```

## Key conventions

- **Confirm before overwrite:** fails closed unless `--yes` is provided or the caller confirms.
- **Record install:** writes or updates `skills.json` in the target scope.
- **No arbitrary command execution:** only copies local directories or downloads archives from URLs.
- **Source-first:** registry names are not directly installable; resolve them to a URL or local path first.

## Maintenance notes

- Target directory detection is delegated to `detect-project-context` for project scope.
- Add archive formats by extending the extraction logic.
- Update the install schema if `skills.json` evolves.
- Keep the confirmation behavior strict to avoid accidental overwrites.
