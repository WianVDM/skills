---
name: handoff
description: "Capture the current session state into a resumable handoff document. Use when the user says 'handoff', '/handoff', 'handoff {key}', '/handoff {key}', 'save a checkpoint', 'continue this later', 'I need to resume this', or 'capture the current state'."
argument-hint: "Optional ticket key or session alias (omit for an unticketed handoff)"
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "2.0"
  scope: global
invocation: user-invoked
disable-model-invocation: true
---

# handoff

Execute the handoff workflow below to capture the current session state into a resumable, chainable handoff document.

## Out of scope

- Do not load, resume, or continue from a previous handoff.
- Do not auto-invoke on context limit or session end.
- Do not create, modify, or execute project artifacts.
- Do not run tests or generate plans.
- Do not hardcode references to specific skills or tools.

## Steps

1. **Detect the context directory.**
2. **Resolve the user argument.** If none, use unticketed mode.
3. **Discover relevant context.** Use the helper script and let the user confirm the artifact list.
4. **Resolve the handoff path and chain position.** Increment sequence if the target exists.
5. **Draft the handoff document.**
   - Distill, do not summarize. Include only: one goal, one current-state sentence, one next action, user clarifications, user preferences, referenced artifacts, and a chain link.
   - Reference full content by path; do not duplicate it.
   - Keep the document under 4k tokens.
   - Completion: the draft is a snapshot a fresh session can act on, not a summary of the chat.

6. **Verify the draft.**
   - Check that "Next" is a single concrete action.
   - Check that "Tried" is a list of `(action → outcome)` pairs, not paragraphs.
   - Check that no artifact content is duplicated inline.
   - Check that the previous handoff is referenced by path, not summarized.
   - Check that the document is under 4k tokens.
   - Completion: every check passes; if not, tighten the draft.

7. **Persist and report.** Write the file and report its path.
8. **Prune old unticketed handoffs.**

## Output

- With ticket key or alias: `.agents/context/handoffs/{key}/handoff-{sequence}.md`
- Without ticket key: `.agents/context/handoffs/unticketed/{timestamp}-handoff.md`

## Scripts

- `scripts/handoff-helper.py` — `discover`, `resolve`, `prune`.

## Dependencies

- Filesystem access to the detected context directory.
- Python 3.
- Optional: git, conversation transcript.
