# Default source configuration

The canonical source package for this setup skill is always:

```text
github.com/WianVDM/skills
```

This resolves to `https://github.com/WianVDM/skills`.

## Source version

By default, the skill syncs to the latest release of `github.com/WianVDM/skills`.

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

The target scope directory may be a symlink farm (for example, `.pi/agent/skills/` resolving to `.agents/skills/`). Before comparing or installing skills, resolve the target path to its canonical storage location. Do not rely on hardcoded personal paths; use the symlink target or filesystem canonicalization.

## Symlink pattern detection

When `list-available-skills` returns installed skills, check whether they are symlinks or regular copies. If any existing skill is a symlink, ask the user whether to follow the symlink pattern for this sync.

- **Follow the symlink pattern** (default): install or update skills as symlinks so the layout matches the existing installation.
- **Install to the canonical target path**: copy skills directly into the resolved target directory.

The resolved pattern is recorded in the context report.

## Network access

The source package is fetched using `git` if available; otherwise `curl` is used as a fallback. If `github.com/WianVDM/skills` is private or rate-limited, set the `GITHUB_TOKEN` environment variable.
