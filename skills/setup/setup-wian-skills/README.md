# setup-wian-skills

Initialize and set up configuration for Wian's skills in the workspace — once, across all installed bundle skills. It never installs or updates skills.

## Usage

```text
/setup-wian-skills
/setup-wian-skills --preview
```

Running `/setup-wian-skills` asks one question first: full setup now, or defer to lazy loading?

- **lazy** (recommended): resolve `shared` keys — the bindings to the global shared config — and let lazy-eligible skills collect their private keys on first use.
- **full**: resolve every key now, shared and private.

## What it does

1. Detects the workspace context and target scope.
2. Discovers installed bundle skills and reads their `config.yaml` declarations.
3. Builds the cross-skill config graph: dedupes shared keys, infers defaults, orders questions.
4. Prompts for the resolve-now set, preserving existing values.
5. Writes `shared.yaml` and delegates per-skill config writes to `initialize-skill`, after approval.
6. Presents the initialization checklist and writes a context report.

## When no skills are installed

The skill stops and prints the install command for you to run yourself:

```text
npx skills@latest add WianVDM/skills --skill '*' -y
```

## Options

- `--preview`: Show the plan and the questions each mode would ask, without writing anything.

## References

See `SKILL.md` and the `references/` directory for the full skill contract.
