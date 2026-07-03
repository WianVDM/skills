---
name: handoff
description: "Snapshot the current session so a fresh session can continue. Use when you need to hand off or checkpoint."
argument-hint: "Optional key or alias"
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "3.0"
  scope: global
invocation: user-invoked
disable-model-invocation: true
---

# handoff

Snapshot the session. Distill what a fresh session needs to continue, then write it to a handoff file.

## Out of scope

Do not resume, modify, or auto-invoke.

## Steps

1. Detect the context directory.
2. Resolve the argument (unticketed if none).
3. Discover relevant artifacts.
4. Resolve the next handoff path.
5. Write and tighten the snapshot: goal, state, next, tried, blockers, user preferences, links, chain. One next action. No duplicates. Under 4k tokens.
6. Report the path.

## Output

- With key: `.agents/context/handoffs/{key}/handoff-{N}.md`
- Without key: `.agents/context/handoffs/unticketed/{timestamp}-handoff.md`

## Dependencies

- Filesystem access.
- Python 3 for `scripts/handoff-helper.py`.
