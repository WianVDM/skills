# handoff

A user-invoked, standalone skill for capturing session state into a resumable, chainable handoff document.

## Quick usage

```
handoff
handoff SHB-283
handoff auth-refactor
save a checkpoint
continue this later
```

The skill writes the handoff document and reports its path. The next session is started by the user or harness using that path.

## What it captures

The handoff is designed for continuation, not just summary. Each document includes:

- The main goal.
- The current task list and status.
- What has been tried and the outcome.
- What failed or is blocked.
- The immediate next action.
- User clarifications and preferences from the session.
- Paths to relevant artifacts with one-line summaries.
- Recommended skills for the next session.
- A link to the previous handoff in the chain.

## Chaining

When you provide a ticket key or session alias, the skill appends to the chain:

```
.agents/context/handoffs/SHB-283/
├── handoff-001.md
├── handoff-002.md
└── handoff-003.md
```

Each handoff references the previous one, so a fresh session can follow the chain back to the start.

## Unticketed handoffs

If you do not provide a key, the handoff is written to:

```
.agents/context/handoffs/unticketed/{timestamp}-handoff.md
```

The directory is pruned to the 10 most recent handoffs by default.

## Helper script

`scripts/handoff-helper.py` provides deterministic subcommands:

- `discover` — list candidate artifacts from the context directory.
- `resolve` — determine the next handoff path, sequence, and previous handoff.
- `prune` — remove older unticketed handoffs beyond the limit.

Example:

```bash
python scripts/handoff-helper.py discover --context-dir .agents/context
python scripts/handoff-helper.py resolve --key SHB-283 --context-dir .agents/context
python scripts/handoff-helper.py prune --context-dir .agents/context --limit 10
```

## Maintenance and versioning

- **Review cadence:** review after 10 real-world uses or whenever a chaining bug is reported.
- **Trigger evals:** test that the skill invokes on all documented triggers and ignores ambiguous phrases.
- **Behavior evals:** test that a 5+ handoff chain preserves enough context for a fresh session to continue.
- **Version bump:** bump the version in `SKILL.md` frontmatter and `handoff_version` when the schema, config, or chaining behavior changes.

## License

Proprietary.
