# Default source configuration

The canonical source package for this setup skill is always:

```text
WianVDM/skills
```

This resolves to [`skills`](https://github.com/WianVDM/skills).

## Installation and updates

The skill uses the Vercel skills CLI to install or update the bundle:

```text
npx skills@latest add WianVDM/skills
```

For updates, the CLI may also be invoked as:

```text
npx skills update
```

The skill selects the appropriate command based on whether the bundle is already installed.

## Source version

By default, the skill syncs to the latest release of `WianVDM/skills`.

To sync to a specific release or tag, use the `--version <tag>` argument:

```text
/setup-wian-skills --version v1.2.3
```

To preview what would be synced without applying changes, use the `--preview` argument:

```text
/setup-wian-skills --preview
/setup-wian-skills --preview --version v1.2.3
```

## Target scope path resolution

The target scope directory may be a symlink farm (for example, `.pi/agent/skills/` resolving to `.agents/skills/`). The skills CLI resolves the correct harness-specific install path. The skill uses `detect-project-context` to locate the canonical config and context directories for writing shared configuration and context reports.

## Network access

The skills CLI fetches the source package from GitHub. If `github.com/WianVDM/skills` is private or rate-limited, set the `GITHUB_TOKEN` environment variable.
