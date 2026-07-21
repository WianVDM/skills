# scripts

## select-install.mjs

Install, update, and remove skills from the `WianVDM/skills` bundle. A wrapper around the [Vercel skills CLI](https://www.npmjs.com/package/skills) — the CLI executes every install, removal, and list operation; this script only replaces the parts of the UX that don't work.

Why it exists: the CLI's interactive picker has no usable per-skill selection indicator and disables search when groups exist (upstream: vercel-labs/skills#439, #992), and the CLI does not resolve skill dependencies. Delete this script when the CLI grows real checkboxes and dependency resolution.

### Running it

From anywhere (downloads the script, then runs it):

```powershell
# PowerShell
iwr https://raw.githubusercontent.com/WianVDM/skills/main/scripts/select-install.mjs -OutFile "$env:TEMP\select-install.mjs"; node "$env:TEMP\select-install.mjs" -g
```

```bash
# bash
curl -sL https://raw.githubusercontent.com/WianVDM/skills/main/scripts/select-install.mjs -o /tmp/select-install.mjs && node /tmp/select-install.mjs -g
```

From a clone of this repo: `node scripts/select-install.mjs -g`.

### Modes

**Install (default, no flags).** A plain-text checklist of the bundle catalog: skills grouped by bundle with an `[x]` per row, your already-installed skills pre-ticked, and the exact CLI command printed for approval before it runs. Use it to install a subset or to change an existing selection.

Selector input: numbers (`3`), ranges (`12-15`), bundle names (`main`, `blocks`, `setup`), `a` = all, `n` = none. Each token toggles. Empty line = done.

**`--remove`.** The same checklist, restricted to skills you have installed from this bundle. Third-party skills are never listed.

**`--update`.** Sync an existing install to the current catalog. No checklist — the selection is derived from what you have installed:

1. Identifies bundle skills via the CLI's lock file (`source: "WianVDM/skills"`), so third-party installs are left alone. Without a lock file it falls back to name matching and warns.
2. Refreshes every installed bundle skill (the CLI's add overwrites in place).
3. Installs missing dependencies — required and recommended, resolved transitively from `skills.json`. Tier propagation follows the weakest link: a required dependency of a recommended dependency is installed as recommended.
4. Reports orphans: bundle-sourced skills that no longer exist in the catalog (renamed or removed upstream). Plain `--update` leaves them installed with a warning; `--clean` removes them.
5. Prints the full plan and the CLI command(s) for approval, then runs them.

### Flag reference

| Flag | Meaning |
|---|---|
| `-g`, `--global` | Global scope (`~/.agents/skills`). Default if you answer `g` at the prompt. |
| `-p`, `--project` | Project scope (`.agents/skills` in the current directory). |
| `--remove` | Remove selected skills (checklist of installed bundle skills). |
| `--update` | Refresh installed bundle skills and install missing dependencies. |
| `--clean` | With `--update`: remove installed bundle skills first, then reinstall. |
| `--with-optional` | With `--update`: also install optional dependencies. |
| `--no-recommended` | With `--update`: required dependencies only. |
| `-a`, `--agent <name>` | Target a specific agent (repeatable), passed through to the CLI. |
| `--print` | Print the CLI command(s) without running anything. |
| `-y`, `--yes` | Skip the final run confirmation. |
| `--source <path>` | Load the catalog from a local `skills.json` instead of GitHub. |
| `-h`, `--help` | Help. |

`--update` and `--remove` are mutually exclusive. `--clean` only makes sense with `--update`.

### `--update` vs `--clean`

The CLI's add overwrites existing files, so a plain `--update` refreshes content but does not delete files that were removed upstream. `--clean` uninstalls the bundle set first, guaranteeing no stale files or orphaned skills remain. Use plain `--update` for routine syncs; use `--clean` after a large version jump or when you suspect drift.

### Why not `skills update`

The CLI's own `skills update` only handles global installs, updates *every* globally installed skill (not just this bundle), and does not resolve dependencies. This script's `--update` is bundle-scoped, works in both scopes, and reconciles dependencies.

### After any update

- Re-run `/setup-wian-skills` in your agent. Config keys may have been added, and reinstalling does not reset existing config in `.agents/config/`.
- Restart the agent harness so it reloads skill files.
- Local edits to installed skill files are overwritten. Keep customizations out of the installed copies; make them in a fork or in project files.

### Requirements

- Node.js 18 or newer (the script uses the built-in `fetch`; no npm dependencies).
- npm/npx on the PATH — the script shells out to `npx skills@latest` for listing, installing, and removing.
- Network access to GitHub for the catalog. Offline fallback: run from a clone of this repo, where the script reads `./skills.json` instead. In that mode dependency resolution still works; the CLI list fallback (`npx skills add WianVDM/skills --list`) provides names only, without dependency data.

## generate-skill-catalog.py

Regenerates `docs/skill-catalog.md` from `skills.json` and each skill's `SKILL.md`. Run it after adding, removing, or renaming a skill. Not needed for installing or updating the bundle.
