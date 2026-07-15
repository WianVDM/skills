# Dependencies

## Required

- **Python 3.10+** — scripts are written in Python 3.

## Required skills

- `worker-contract` — return contract used if the block is invoked through a subagent.
- `context-reports` — conventions for context directory layout and report schemas.
- `detect-project-context` — discover project root, config dir, and context dir.
- `tool-discovery` — find the best `pr-source` adapter when resolving a PR to a branch or commit.

## Recommended

None.

## Optional

- **git** — used to detect the current branch and repo when not provided.

## Binaries

- Python 3.10+.
- `git` (optional) for current branch/repo detection.

## Consumed references

- Git remote output (if git is available).
- `{config_dir}/shared.yaml` (optional) for `repo` default.

## Produced artifacts

None. This block is read-only.
