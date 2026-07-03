---
name: handoff
description: "Capture the current session state into a resumable handoff document. Use when the user says 'handoff', 'save a checkpoint', 'continue this later', 'I need to resume this', or 'capture the current state'."
argument-hint: "Ticket key or session alias (optional)"
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "2.0"
  scope: global
invocation: user-invoked
disable-model-invocation: true
---

# handoff

Capture the current session state into a concise, resumable handoff document so a fresh session can continue the work. The document links to previous handoffs from the same logical session, preserving context across 5+ chained sessions without re-reading the entire conversation history.

## When to use

- The user says `handoff` or `handoff {key}`.
- The user says `save a checkpoint` or `continue this later`.
- The user says `I need to resume this` or `capture the current state`.
- The session is ending or context is running low and the user wants a clean continuation point.

## Out of scope

- This skill does **not** load, resume, or continue from a previous handoff. The user or harness uses the reported path to start the next session.
- This skill does **not** auto-invoke on context limit or session end.
- This skill does **not** create, modify, or execute project artifacts.
- This skill does **not** run tests, generate plans, or make decisions for the user.
- This skill does **not** hardcode references to specific skills or tools. It consumes any artifact by path, not by source.

## Dependencies

- Filesystem access (read/write) to the detected context directory.
- Python 3 for `scripts/handoff-helper.py`.
- Optional: git, for branch context if available. The skill does not require it.
- Optional: conversation transcript access, if the harness provides it. The skill degrades gracefully without it.

## Steps

1. **Detect the context directory.**
   - Completion: a writable context directory is identified.
   - Failure: stop and explain why no context directory was found.

2. **Resolve the user argument.**
   - If no argument is given, use unticketed mode.
   - If an argument is given, treat it as a ticket key or session alias and normalise it for use as a directory name.
   - Completion: a target key/alias and mode are chosen.

3. **Discover relevant context.**
   - Run the helper script to list candidate artifacts from the context directory and recent conversation references.
   - Let the user confirm, add, or remove items from the candidate list.
   - Completion: a final list of referenced artifacts is agreed on.

4. **Resolve the handoff path and chain position.**
   - Run the helper script to determine the sequence number, the previous handoff path, and the output path.
   - If the target file already exists, increment the sequence; do not overwrite.
   - Completion: an output path is ready.

5. **Draft the handoff document.**
   - Fill the schema: goal, task list, tried/failed/next, user clarifications, user preferences, referenced artifacts, recommended skills, and chain history.
   - Keep the document in the 4k–8k token range. Reference full artifacts by path; do not duplicate them.
   - Completion: a draft matching the schema is ready.

6. **Persist and report.**
   - Write the handoff to the resolved path.
   - Report the path and a one-line summary to the user.
   - Completion: the file exists at the reported path and the user can see the summary.

7. **Prune old unticketed handoffs (unticketed mode only).**
   - Run the helper script to remove unticketed handoffs beyond the configured limit.
   - Completion: the unticketed directory contains at most the configured number of handoffs.

## Handoff document schema

### Frontmatter

```yaml
---
handoff_version: "2.0"
ticket_key: "SHB-283" # omitted for unticketed handoffs
session_alias: "auth-refactor" # optional, user-supplied readable alias
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

## Path conventions

- With ticket key or session alias: `.agents/context/handoffs/{key}/handoff-{sequence}.md`
- Without ticket key: `.agents/context/handoffs/unticketed/{timestamp}-handoff.md`

The base directory `.agents/context` is detected using the project-layout rules. If it does not exist, the skill falls back to the current working directory and warns the user.

Unticketed handoffs are pruned to the most recent 10 by default. The user can override this limit or supply an alias to convert an unticketed chain into a keyed chain.

## Scripts

- `scripts/handoff-helper.py` — deterministic helper with subcommands `discover`, `resolve`, and `prune`. See the script docstring for usage and return schemas.

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
