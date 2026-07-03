---
skill: handoff
version: "2.0"
timestamp: 2026-07-03T00:00:00Z
result: pass
---

# Handoff self-audit

## Summary

The v2.0 design passes the fundamentals checklist. It is a single, well-bounded, standalone skill with deterministic context discovery, a chainable output schema, and clear failure modes. The skill is intentionally write-only: it reports the handoff path but does not resume sessions.

## Checks

- [x] **One core objective.** The skill owns exactly one domain: capturing session state into a resumable handoff document.
- [x] **Explicit out-of-scope.** Out-of-scope section lists auto-invocation, artifact mutation, plan generation, and harness auto-resume.
- [x] **Explicit dependencies.** Filesystem, Python 3, optional git, optional conversation transcript are declared.
- [x] **No secrets in files.** No secrets required.
- [x] **Destructive actions confirmed.** Overwrite is gated by explicit confirmation or auto-incremented sequence.
- [x] **Harness-agnostic and project-agnostic.** No harness commands, no hardcoded project paths; context directory is detected.
- [x] **No hidden assumptions.** Assumptions (context dir exists, Python 3 available) are declared; skill fails closed if missing.
- [x] **Appropriate skill type.** Standalone with one helper script matches the problem size.
- [x] **Form matches domain.** Instruction-heavy SKILL.md with a clear schema; README for examples.
- [x] **Steps have completion criteria.** Design phases end with checkable conditions.
- [x] **Description is trigger-rich.** Triggers: `handoff`, `handoff {key}`, `save a checkpoint`, `continue this later`, `capture the current state`.
- [x] **No duplicate triggers.** None overlap with other known skills.
- [x] **Leading word used.** `Capture` anchors the behavior.
- [x] **Negation pairs.** Every negation is paired with a positive directive in the SKILL.md draft (e.g., “Do not overwrite existing handoffs; increment sequence or confirm first”).
- [x] **No vague guideline soup.** Each guideline is tied to a concrete schema section or script behavior.
- [x] **No no-op lines.** Each design element changes behavior or documents a required decision.
- [x] **Progressive disclosure.** Detail lives in README and script docs; SKILL.md stays focused on workflow and schema.
- [x] **State and reports documented.** Handoff document schema, path conventions, and chaining logic are documented.
- [x] **Worker contract defined.** Not applicable; no subagents.
- [x] **Scripts for deterministic logic.** `handoff-helper.py` handles discovery, path resolution, and pruning.
- [x] **Review cadence planned.** Eval checklist included in README; version bump on schema/behavior changes.

## Anti-over-complication checks

- **Does this need to be a skill?** Yes. The schema, chaining, and context discovery benefit from a shared, predictable shape.
- **Does it need all proposed features?** Yes for v2.0; chaining and context discovery are core to the user’s stated intent.
- **Are proposed building blocks actually reusable?** No premature abstraction; only one helper script.
- **Does it need state?** Yes, chaining is stateful by definition.
- **Does it need config?** Detection covers most cases; session alias is optional.
- **Does it need to delegate?** No, the work is small enough for inline execution with one helper script.
- **Does it need a new subagent?** No.
- **Does it need a dedicated reference file?** No, the schema and usage examples fit in SKILL.md and README.

## Overrides

None.

## Blockers

None.
