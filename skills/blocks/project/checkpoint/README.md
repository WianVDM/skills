# checkpoint

A building-block skill that maintains phase checklists, current focus, and resume state for long-running conductor skills. It only reads, validates, and writes state — it does not make decisions or ask the user questions.

See [`SKILL.md`](SKILL.md) for the full input/output contract, state file schema, and operations.

## Quick usage

Create a checkpoint:

```text
Run checkpoint: create state for owner debrief, key OC-4644, phases [Bootstrap, Gather evidence, Build context graph].
```

Update and resume:

```text
Run checkpoint: update state at {context_dir}/debrief/OC-4644/state.md, completed_phase "Gather evidence", current_focus "Build context graph".
Run checkpoint: resume from {context_dir}/debrief/OC-4644/state.md.
```

The deterministic helper can also be invoked directly:

```bash
echo '{"operation":"create","state_path":".agents/context/debrief/OC-4644/state.md","owner":"debrief","key":"OC-4644","phases":["Bootstrap","Gather evidence"]}' | python scripts/checkpoint.py
```
