# handoff

A user-invoked, standalone skill for capturing session state into a resumable, chainable handoff document.

## Quick usage

```
handoff
/handoff
handoff ISSUE-123
/handoff ISSUE-123
handoff auth-refactor
save a checkpoint
continue this later
```

The skill writes the handoff document and reports its path. The next session is started by the user or harness using that path.

## What it captures

The handoff is designed for continuation, not summary. Each document includes:

- **Goal** — the single main objective.
- **Current state** — one sentence describing where the session is right now.
- **Task list** — tasks with status: done, in-progress, blocked, pending.
- **Tried** — what has been attempted this session, as `(action → outcome)` pairs.
- **Blockers** — failures, errors, and unresolved issues.
- **Next** — the single immediate next action.
- **Changes this session** — deltas from the previous handoff.
- **User clarifications** — explicit decisions or answers the user gave.
- **User preferences** — preferences stated in this session.
- **Referenced artifacts** — paths to useful files with one-line summaries.
- **Recommended skills** — skills that may be useful next.
- **Chain** — link to previous handoff and one-line summary of prior sessions.

## Handoff document schema

### Frontmatter

```yaml
---
handoff_version: "2.0"
ticket_key: "ISSUE-123"            # omitted for unticketed handoffs
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
2. **Current state** — one sentence describing where the session is right now.
3. **Task list** — tasks with status: done, in-progress, blocked, pending.
4. **Tried** — attempts and outcomes this session, as `(action → outcome)` pairs.
5. **Blockers** — failures, errors, and unresolved issues.
6. **Next** — the single immediate next action.
7. **Changes this session** — deltas from the previous handoff.
8. **User clarifications** — explicit decisions or answers the user gave.
9. **User preferences** — preferences stated in this session.
10. **Referenced artifacts** — paths to useful files with one-line summaries.
11. **Recommended skills** — skills that may be useful next, listed without invocation syntax.
12. **Chain** — link to previous handoff and one-line summary of prior sessions.

## Chaining

When you provide a ticket key or session alias, the skill appends to the chain:

```
.agents/context/handoffs/ISSUE-123/
├── handoff-001.md
├── handoff-002.md
└── handoff-003.md
```

Each handoff references the previous one, so a fresh session can follow the chain back to the start. Record only deltas in the current handoff; never duplicate the body of previous handoffs.

## Compression rules

To keep handoffs concise and loss-resistant:

- **Inline** only what the next session needs immediately: goal, current state, next action, user preferences, and clarifications.
- **Reference** all artifacts by path. Never duplicate full content.
- **Chain** previous handoffs by path. Summarize older sessions in one line; never duplicate their body.
- **Use deltas**: record what changed in this session, not the full history.
- **Target**: keep each handoff under 4k tokens. If a handoff exceeds 8k, summarize older chain links.

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
python scripts/handoff-helper.py resolve --key ISSUE-123 --context-dir .agents/context
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
