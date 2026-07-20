# Bundle identity and install command

The canonical source package for this setup skill is always:

```text
WianVDM/skills
```

This resolves to [`skills`](https://github.com/WianVDM/skills).

## Bundle membership

Determine which installed skills belong to the bundle from the installer's lock metadata (source `WianVDM/skills`) when it is available. Otherwise treat the skills co-installed in the same scope as `setup-wian-skills` itself as candidates, and confirm the resulting set with the user before building the config graph.

## When no bundle skills are installed

This skill never installs skills. Stop and hand the user the exact command to run themselves:

```text
npx skills@latest add WianVDM/skills --skill '*' -y
```

Scope and agent selection are the user's choice: add `--global` for user scope, omit it for project scope, and add `-a <agent>` to target specific agents. A specific release installs as `WianVDM/skills@<tag>`.

## When the interactive picker does not work

The CLI's interactive picker has no usable per-skill selection indicator (upstream: vercel-labs/skills#439). Offer the checkbox wrapper instead — no clone needed:

```powershell
iwr https://raw.githubusercontent.com/WianVDM/skills/main/scripts/select-install.mjs -OutFile "$env:TEMP\select-install.mjs"; node "$env:TEMP\select-install.mjs" -g
```

```bash
curl -sL https://raw.githubusercontent.com/WianVDM/skills/main/scripts/select-install.mjs -o /tmp/select-install.mjs && node /tmp/select-install.mjs -g
```

It fetches the catalog, pre-ticks installed skills, and runs the CLI with the user's selection. Requires Node.js 18+ and npm/npx on the PATH. From a clone of the skills repo, `node scripts/select-install.mjs -g` does the same and works offline.

## Target scope path resolution

The config directory may live behind symlinks (for example, `.pi/agent/skills/` resolving to `.agents/skills/`). The skill uses `detect-project-context` to locate the canonical config and context directories for writing shared configuration and context reports.
