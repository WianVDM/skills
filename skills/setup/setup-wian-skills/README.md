# setup-wian-skills

Sync skills from `github.com/WianVDM/skills` into the current workspace and resolve shared configuration once.

## Usage

```text
/setup-wian-skills
/setup-wian-skills --preview
/setup-wian-skills --version <tag>
```

## What it does

1. Detects the existing installation pattern (symlink or copy) and asks whether to follow it.
2. Builds a sync plan from the latest (or pinned) source release and asks for explicit approval before applying changes.
3. Resolves conflicts with locally modified or same-name skills.
4. Gathers shared configuration once and prompts for missing keys.
5. Applies the sync atomically, rolls back on failure, and validates every installed skill.
6. Presents the initialization checklist and writes a context report.

## Options

- `--preview`: Show the sync plan and configuration questions without applying changes.
- `--version <tag>`: Sync a specific release or tag instead of the latest.

## References

See `SKILL.md` and the `references/` directory for the full skill contract.
