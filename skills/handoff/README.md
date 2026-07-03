# handoff

A user-invoked, standalone skill for capturing session state into a resumable, chainable handoff document.

## Quick usage

```
handoff
/handoff
handoff SHB-283
/handoff SHB-283
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

## Handoff document schema

### Frontmatter

```yaml
---
handoff_version: "2.0"
ticket_key: "SHB-283"            # omitted for unticketed handoffs
session_alias: "auth-refactor"   # optional, user-supplied readable alias
sequence: 3
previous_handoff: "handoff-002.md"
timestamp: "2026-07-03T14:22:11Z"
session_id: "<stable-session-id>"
generated_by: "handoff skill v2.0"
summary: "OAuth refactor: middleware extracted, token validation tests failing, next step is fix date parser."
---
```

### Body sections

1. **Goal** — the single main objective.
2. **Task list** — tasks with status: done, in-progress, blocked, pending.
3. **What has been tried** — attempts and outcomes.
4. **What failed / blockers** — failures, errors, and unresolved issues.
5. **What is next** — the immediate next action.
6. **User clarifications** — explicit decisions or answers the user gave.
7. **User preferences** — preferences stated in this session (style, tools, format, etc.).
8. **Referenced artifacts** — paths to useful files with one-line summaries.
9. **Recommended skills** — skills that may be useful next, listed without invocation syntax.
10. **Chain history** — one-line summary of previous handoffs and a link to the previous document.

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

## Failure modes

- If the context directory is not writable: stop and explain.
- If the helper script is missing or fails: stop and report the error; do not write a partial handoff.
- If no relevant context can be discovered: still produce a handoff using the user-provided focus and conversation summary, but warn that the artifact list is empty.
- If the target file already exists: increment the sequence number instead of overwriting.

## Security

- No secrets are stored in skill files.
- Writes are limited to the detected context directory.
- The helper script does not execute discovered files.
- Overwrites are never silent; the sequence is incremented or the user is asked.
- Prefer read-only investigation when scanning for context.

## Maintenance and versioning

- **Review cadence:** review after 10 real-world uses or whenever a chaining bug is reported.
- **Trigger evals:** test that the skill invokes on all documented triggers and ignores ambiguous phrases.
- **Behavior evals:** test that a 5+ handoff chain preserves enough context for a fresh session to continue.
- **Version bump:** bump the version in `SKILL.md` frontmatter and `handoff_version` when the schema, config, or chaining behavior changes.

## License

Proprietary.
