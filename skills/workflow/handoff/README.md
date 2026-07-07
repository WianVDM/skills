# handoff

Write a session handoff snapshot for an optional key, so a fresh session can continue.

## Usage

- `handoff` — write an unticketed handoff.
- `handoff {key}` — write a handoff tied to a ticket key or session alias.

## Where the file is written

The snapshot is written under the detected project context directory:

- `{context_dir}/handoffs/unticketed/{timestamp}-handoff.md`
- `{context_dir}/handoffs/{normalized-key}/handoff-{N}.md`

Keys are normalized to lowercase letters, digits, and hyphens for use as directory names. For example, `ABC-123` becomes `abc-123`.

## How it works

The agent uses `scripts/handoff-helper.py` to resolve the next unique path and to find the previous handoff for the chain. The helper never overwrites or deletes existing handoffs.

## Resuming from a handoff

A new session can continue by loading the latest handoff file, or by using a context-resumption skill such as `context-reports`.
