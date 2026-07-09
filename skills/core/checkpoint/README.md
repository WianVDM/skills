# checkpoint

`checkpoint` is a building-block skill that maintains phase checklists, current focus, and resume state for long-running conductor skills. It provides reliable state management for any conductor that runs across multiple turns or needs to survive context compaction.

## What it does

- Creates a markdown state file with a frontmatter envelope and a phase checklist.
- Updates phase status, current focus, and last completed action after each sub-step.
- Appends to a session history table and archives oldest rows when the limit is exceeded.
- Resumes from an existing state file without modifying it.
- Validates state file consistency and reports corruption or mismatches.

`checkpoint` does not make decisions, conduct research, or ask the user questions. It only reads, validates, and writes state.

## How to use it

Call `checkpoint` from a conductor skill when you need to track progress or resume work:

```text
Run checkpoint: create state for owner debrief, key OC-4644, phases [Bootstrap, Gather evidence, Build context graph, Resolve ambiguities, Baseline, Synthesize, Present].
```

```text
Run checkpoint: update state at {context_dir}/debrief/OC-4644/state.md, completed_phase "Gather evidence", current_focus "Build context graph", last_action "Ticket researcher returned normalized data."
```

```text
Run checkpoint: resume from {context_dir}/debrief/OC-4644/state.md.
```

The deterministic helper script can also be invoked directly:

```bash
echo '{"operation":"create","state_path":".agents/context/debrief/OC-4644/state.md","owner":"debrief","key":"OC-4644","phases":["Bootstrap","Gather evidence"]}' | python scripts/checkpoint.py
```

## State file

The state file is a markdown document with YAML frontmatter and a structured body. It lives at the caller-provided `state_path`. Session history is archived to `{state_path}.history.md` when the configured row limit is exceeded (default 20 rows).

## Skill metadata

| Attribute | Value |
|---|---|
| Type | Building-block |
| Invocation | Model-invoked |
| Version | 1.0.0 |
| Depends on | `context-reports` |
