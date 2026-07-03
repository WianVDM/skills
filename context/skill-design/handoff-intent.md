---
skill: handoff
version: "2.0"
timestamp: 2026-07-03T00:00:00Z
intent: redesign
status: clarifying
---

# Handoff intent note

## Problem

A single agent session can run out of context or be interrupted while working on a long-running task. The user needs a way to continue work in a fresh session without losing the accumulated context, decisions, failures, and preferences from the original session. Existing conversation summaries are too lossy; what is needed is a dense, resumable checkpoint.

The skill must also support **chaining**: a task may span 5+ sessions, each producing a handoff that references the previous one, so the latest session still has full historical context without re-reading the entire conversation history.

## Trigger

User-invoked. The user says things like:
- "handoff"
- "I need to continue this later"
- "save a checkpoint"
- `handoff {key}` — writes the next handoff in the `{key}` chain and reports the path.

## Success criteria

- The produced handoff document captures enough context that a fresh session can continue exactly where the previous one stopped.
- It is concise but loss-resistant: task list, main goal, tried/failed/next actions, user clarifications, user preferences, and relevant artifacts are preserved.
- It can chain to previous handoffs from the same logical session, so history survives across 5+ handoffs.
- It does not hardcode references to specific skills or tools (e.g., verify-branch); it ingests any relevant context generated in the current session regardless of source.
- It is barebones and standalone: minimal moving parts, no heavy conductor workflow, no unnecessary subagents.

## Confirmed decisions

Updated on 2026-07-03.

- Context discovery: Option C — scan conversation + context dir, user can override.
- Storage: Option D — `.agents/context/handoffs/{ticket-key}/handoff-{N}.md` or `.agents/context/handoffs/unticketed/{timestamp}-handoff.md`.
- Default mode without ticket key: Option C — timestamped files in unticketed dir, with pruning.
- Consumption: Option A only — report the handoff path to the user; loading/resuming is outside the skill's scope.
- Content strategy: Option C — inline critical context, reference the rest.
- Size target: 4k–8k tokens.
- Invocation: user-invoked only.
- Skill type: standalone with one helper script.
- Leading word: Capture.

## Constraints

- Standalone skill, as lightweight as possible.
- No hardcoded skill-specific artifact references.
- Must work both with and without a ticket key.
- Output must be optimized for model consumption in a fresh session, not just human reading.
- Must be able to discover relevant context from the session without requiring the user to manually list every artifact.

## Skill warranted?

Yes. This is a load-bearing, recurring problem that benefits from a shared shape and predictable output schema. A plain prompt or ad-hoc summary would be too inconsistent and too lossy for multi-session chains.
