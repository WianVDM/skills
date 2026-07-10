---
name: handoff
description: "Write a session handoff snapshot for an optional key, so a fresh session can continue."
version: 1.0.1
invocation: user-invoked
disable-model-invocation: true
metadata:
  author: Wian van der Merwe
  tags: [workflow, building-block, handoff, context]
---

# handoff

## Purpose

Distill what a fresh session needs to continue into a single handoff snapshot.

## Type

Building block.

## In scope

- Detect the context directory and resolve the key.
- Write a single snapshot file capturing the elements listed in the template.
- Report the written path.

## Out of scope

- Do not resume, modify, or auto-invoke.
- Do not delete, prune, or archive existing handoffs.
- Do not read or write application code.

## Portability

- Global skill; works in any project with a writable context directory.
- The helper detects `.agents/context` in the current working directory or any ancestor, then falls back to the current working directory.
- If `detect-project-context` is available, the agent may use it to obtain the context directory and pass it to the helper with `--context-dir`.
- Stop and report an error if no writable context directory is found.

## Security

- The skill writes only new files; it never overwrites or deletes existing handoffs.
- The user's explicit invocation of `handoff` is the approval to write the new snapshot.

## Steps

1. **Detect the context directory.** If `detect-project-context` is available, use it to get the context directory. Otherwise let `scripts/handoff-helper.py` detect it by running without `--context-dir`. The directory must be writable; if not, stop and report the error.
2. **Resolve the key.** Use the key or alias if provided; otherwise default to `unticketed`. Keys are normalized to lowercase letters, digits, and hyphens for use as directory names.
3. **Resolve the next handoff path.** Run `scripts/handoff-helper.py [--context-dir <dir>] resolve [--key <key>]` to pick a unique filename and obtain the previous handoff name.
4. **Populate the snapshot from the template.** Using `references/HANDOFF_TEMPLATE.md`:
   - Write a one-sentence goal.
   - Summarize the current state and what has been completed.
   - State the single next action.
   - List tried approaches and their outcomes.
   - List blockers, or `None`.
   - List user preferences or constraints stated in the session.
   - Add annotated links to relevant artifacts; each link must include a one-line description.
   - If the helper returned a `previous_handoff`, link to it in the Chain section.
5. **Remove duplicate links and tighten the snapshot.** Ensure the next session can act without reading the linked artifacts.
6. **Write the snapshot and report the path.** Write the populated snapshot to the resolved path and return the absolute path.

## Output

- With key: `{context_dir}/handoffs/{normalized-key}/handoff-{N}.md`
- Without key: `{context_dir}/handoffs/unticketed/{timestamp}-handoff.md`

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).
