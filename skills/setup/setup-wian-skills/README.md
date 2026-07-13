# setup-wian-skills

Prepare the workspace to use Wian's skills by installing or updating the bundle via the Vercel skills CLI, then resolving shared configuration once.

## Usage

```text
/setup-wian-skills
/setup-wian-skills --configure
/setup-wian-skills --preview
/setup-wian-skills --version <tag>
```

## What it does

1. Detects the workspace context and target scope.
2. Uses the Vercel skills CLI to install or update the `WianVDM/skills` bundle.
3. Warns about locally modified skills and asks whether to proceed.
4. Gathers shared configuration once and prompts for missing keys.
5. Applies the config and validates every installed skill.
6. Presents the initialization checklist and writes a context report.

## Options

- `--configure`: Skip the CLI install/update and only resolve shared config.
- `--preview`: Show the plan and configuration questions without applying changes.
- `--version <tag>`: Install or update to a specific release or tag instead of the latest.

## References

See `SKILL.md` and the `references/` directory for the full skill contract.
