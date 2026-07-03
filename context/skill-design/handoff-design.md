---
skill: handoff
version: "3.0"
timestamp: 2026-07-03T00:00:00Z
status: design
---

# Handoff skill design (v3.0)

## Objective

Snapshot the current session and write it to a chainable handoff file so a fresh session can continue without re-reading the entire conversation history.

## Boundaries

### In scope

- Snapshot the current session state.
- Discover relevant artifacts from the current session.
- Chain to previous handoffs from the same logical session.
- Persist the snapshot to a deterministic, project-local path.
- Report the path to the user.

### Out of scope

- Auto-invoking on context limit or session end.
- Creating, modifying, or executing project artifacts.
- Running tests, generating plans, or making decisions for the user.
- Resuming a session without a handoff path.
- Hardcoding references to specific skills or tools.

## Skill type, invocation, and portability

- **Type:** Standalone, with one deterministic helper script.
- **Invocation:** User-invoked.
- **Scope:** Global.
- **Leading word:** **Snapshot** — anchors the behavior: capture a session state, then persist it.

## Triggers

- `handoff`
- `handoff {key}`
- `save a checkpoint`
- `continue this later`
- `I need to resume this`
- `capture the current state`

## Argument handling

- No argument → unticketed chain.
- Argument → ticket key or session alias, normalised for use as a directory name.
- Optional explicit artifact paths or notes are merged with discovered context.

## Consumption model

Write-only. The skill produces the handoff file and reports its path. Resuming is performed by the user or harness in the new session.

## Handoff document schema

A snapshot, not a summary. Inline only what the next session needs to act; reference everything else by path.

- **Goal** — the single main objective.
- **Current state** — one sentence describing where the session is right now.
- **Next** — the single immediate next action.
- **Tried** — attempts this session as `(action → outcome)` pairs.
- **Blockers** — failures, errors, and unresolved issues.
- **User preferences** — decisions, preferences, and clarifications from the user.
- **Referenced artifacts** — links to useful files with one-line summaries.
- **Chain** — link to previous handoff and one-line summary of prior sessions.

## Path conventions

- With key or alias: `.agents/context/handoffs/{key}/handoff-{sequence}.md`
- Without key: `.agents/context/handoffs/unticketed/{timestamp}-handoff.md`

The `.agents/context` directory is detected; if missing, the skill falls back to the current working directory and warns.

Unticketed handoffs are pruned to the most recent 10 by default.

## Scripts

- `scripts/handoff-helper.py` — `discover`, `resolve`, `prune`.

## Dependencies

- Filesystem access (read/write).
- Python 3.
- Optional: git, conversation transcript.

## Failure modes

- Unwritable context directory: fail closed with explanation.
- Missing helper script: report and stop.
- No discovered context: still produce snapshot with user-provided focus, but warn.
- Existing target file: increment sequence; never overwrite.

## Security

- No secrets in skill files.
- Writes only to the detected context directory.
- No execution of discovered files.
- No silent overwrites.

## Directory structure

```
handoff/
├── SKILL.md
├── README.md
└── scripts/
    └── handoff-helper.py
```
