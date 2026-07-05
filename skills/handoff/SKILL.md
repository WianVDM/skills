---
name: handoff
description: "Write a session handoff snapshot so a fresh session can continue."
license: Proprietary
invocation: user-invoked
disable-model-invocation: true
metadata:
  author: Wian van der Merwe
  tags: [session-management, checkpoint, handoff]
  verification_level: declared
---

# handoff

## Purpose

Distill what a fresh session needs to continue into a single handoff snapshot.

## Type

Building block.

## In scope

- Detect the context directory, resolve the key, and discover relevant artifacts.
- Write a single snapshot file capturing the elements listed below.
- Report the written path.

## Out of scope

- Only write the snapshot; do not resume, modify, or auto-invoke.
- Do not delete, prune, or archive existing handoffs.
- Do not read or write application code.

## Portability

- Global skill; works in any project with a writable context directory.
- Prefer `detect-project-context` if it is available; otherwise the helper detects `.agents/context` or falls back to the current working directory.
- Stop and report an error if no writable context directory is found.

## Security

- The skill writes only new files; it never overwrites or deletes existing handoffs.

## Steps

1. **Detect the context directory.** It must be a valid, writable path; otherwise stop and report.
2. **Resolve the argument.** Use the key or alias if provided; otherwise default to `unticketed`.
3. **Discover relevant artifacts.** Scan the context directory for recent `.md` files.
4. **Resolve the next handoff path.** Run `scripts/handoff-helper.py resolve` to pick a unique filename.
5. **Draft and verify the snapshot.** Use `references/HANDOFF_TEMPLATE.md`. Include: goal, current state, one next action, tried approaches, blockers, user preferences, annotated links, and chain. Remove duplicates. Ensure the next session can act without reading the linked artifacts. Stay within the configured token budget (default 8,000 tokens).
6. **Report the path.** Return the absolute path to the new handoff file.

## Output

- With key: `{context_dir}/handoffs/{key}/handoff-{N}.md`
- Without key: `{context_dir}/handoffs/unticketed/{timestamp}-handoff.md`

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).
