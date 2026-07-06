# Default source configuration

The default source package for this setup skill is:

```text
WianVDM/skills
```

This resolves to `https://github.com/WianVDM/skills`.

Override the source by passing a different package argument when invoking the skill:

```text
/setup-wian-skills <owner>/<repo>
```

## Target scope path resolution

The target scope directory may be a symlink farm (for example, `.pi/agent/skills/` resolving to `.agents/skills/`). Before comparing or installing skills, resolve the target path to its canonical storage location. Do not rely on hardcoded personal paths; use the symlink target or filesystem canonicalization.
