# Project conventions

This file is the **tracked, GitHub-published** counterpart to `AGENT.md`.
`AGENT.md` holds the same conventions locally for this workspace, but it is
`.gitignore`d so it does not get pushed. This file exists so that the project
rules are still visible to anyone browsing the repository.

## Skill versioning

This repo uses a simple, personal versioning scheme for all skills and skill artifacts.

- All skills and skill artifacts start at **v1.0.0**.
- Versions are always three numbers: `vMAJOR.MINOR.PATCH`.
- Incrementation is strictly right-to-left, with no semantic meaning attached to major, minor, or patch:
  - `v1.0.0` → `v1.0.1` → ... → `v1.0.9` → `v1.1.0`
  - `v1.1.9` → `v1.2.0`
  - `v1.9.9` → `v2.0.0`
- The next version is always computed from the **latest published version on GitHub**, not from the current committed version in the working tree.
- A version is bumped **once per published release**. If a skill is at `v1.0.1` on GitHub and we make multiple commits before publishing again, those commits stay at `v1.0.1`. The next published release bumps to `v1.0.2`.

When updating a skill, read its latest published version from GitHub, increment once, and do not bump again until the next publish.
