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

## Target scope path resolution

The config directory may live behind symlinks (for example, `.pi/agent/skills/` resolving to `.agents/skills/`). The skill uses `detect-project-context` to locate the canonical config and context directories for writing shared configuration and context reports.
