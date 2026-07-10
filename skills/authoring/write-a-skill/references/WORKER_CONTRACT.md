# Worker return contract

For the canonical worker return contract, forbidden actions, return format, and scope boundaries, see the `worker-contract` skill (located via the detected skills directory). The local subagent composition layer is in `subagents/_TEMPLATE.md`.

This file contains only the `write-a-skill`-specific addendum.

## write-a-skill addendum

- **Only `draft-skill-md` writes final skill files.** Other workers analyze, classify, or suggest, but they do not create, overwrite, or delete skill files under `skills/` or `.agents/skills/`.
- **Workers do not install or run third-party tools.** The conductor uses `install-skill` or the harness tools; workers do not invoke shell commands that mutate project state.
