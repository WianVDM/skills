# Worker return contract

For the general worker return contract and the rationale behind it, see the `worker-contract` skill (located via the detected skills directory).

## write-a-skill specific addendum

- **Only `draft-skill-md` writes final skill files.** Other workers analyze, classify, or suggest, but they do not create, overwrite, or delete skill files under `skills/` or `.agents/skills/`.
- **Workers do not install or run third-party tools.** The conductor uses `install-skill` or the harness tools; workers do not invoke shell commands that mutate project state.
