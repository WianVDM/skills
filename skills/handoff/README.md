# handoff

Snapshot the session for continuation.

Usage: `handoff` or `handoff {key}`

Output:
- `.agents/context/handoffs/{key}/handoff-{N}.md`
- `.agents/context/handoffs/unticketed/{timestamp}-handoff.md`

Inline only what the next session needs to act. Reference everything else by path.
