---
name: handoff
description: "Write a session handoff snapshot in multiple passes, from high-level overview to detailed context, so a fresh session can continue."
invocation: user-invoked
depends:
  - detect-project-context
  - context-reports
---

# handoff

## Purpose

Write a session handoff snapshot that a fresh session can continue from.

## Type

Conductor. It coordinates multiple internal synthesis passes and writes a shared context report.

## In scope

- Detect the context directory and resolve the key.
- Load or initialize handoff configuration.
- Run a multi-pass handoff at quick, standard, or thorough level.
- Write the snapshot to the canonical context-report location.
- Archive an existing handoff file for the same key before writing a new one.

## Out of scope

- Do not resume, modify, or auto-invoke.
- Do not delete, prune, or archive existing handoff files beyond the single latest file for a key.
- Do not read or write application code.

## Portability

- Uses `detect-project-context` if available, otherwise detects `.agents/context` or the current working directory.
- Configuration is stored in `.agents/config/handoff.yaml`.

## Configuration

The skill uses the shared config keys and skill-specific keys declared in `config.yaml`.

### Shared keys

- `agents.context_dir` — directory for cross-skill context reports.
- `agents.config_dir` — directory for skill configuration files.

### Skill-specific keys

- `handoff.default_level` — `quick`, `standard`, or `thorough` (default: `standard`).
- `handoff.archive_old` — archive the existing handoff before writing a new one (default: `true`).
- `handoff.include_chain` — include a link to the previous handoff in the new one (default: `true`).

## Initialization

On first run in a project, initialize the skill:

1. **Detect the context and config directories.** If `detect-project-context` is available, use it to get the config and context directories. Otherwise let the helper detect them.
2. **Propose config.** Run `scripts/handoff-helper.py initialize` to propose the default config.
3. **Confirm with the user.** Ask whether to accept the defaults.
4. **Write config.** If approved, run `scripts/handoff-helper.py initialize --approve`.
5. **Report readiness.** Tell the user what was configured and any remaining manual steps.

If the config file already exists, skip initialization unless the user asks to reconfigure.

## Lazy loading

- Required capabilities (Python 3.10+, writable context directory) are checked at initialization.
- `detect-project-context` is evaluated lazily: the skill uses it only when it needs to locate the context directory and falls back to the helper's own detection when the skill is not available.
- `context-reports` is a recommended vocabulary reference; the skill follows its conventions but does not require it at runtime.

## Levels

| Level        | Command            | Passes |
| ------------ | ------------------ | ------ |
| **quick**    | `handoff quick`    | 1      |
| **standard** | `handoff`          | 4      |
| **thorough** | `handoff thorough` | 5      |

If the user does not specify a level, use `handoff.default_level` from config.

## Steps

1. **Initialize if needed.** Check for `.agents/config/handoff.yaml`. If it is missing, run the initialization phase and ask for approval before writing it.
2. **Determine the level.** Use the user-provided level or the configured default.
3. **Resolve the output path.** Run `scripts/handoff-helper.py resolve [--context-dir <dir>] [--config-dir <dir>] [--key <key>]`. The helper archives the existing file if `handoff.archive_old` is `true`.
4. **Populate the snapshot.** Using `references/HANDOFF_TEMPLATE.md`:
   - **Pass 1 — Segment and overview:** Identify the major phases of the session. For each phase, write a heading and a 1–2 sentence summary. The first section should capture the origin and goal; the last section should capture the current state.
   - **Pass 2 — Expand:** For each section, add what was done, what was learned, the files or tools involved, and any user preferences or constraints expressed.
   - **Pass 3 — Zoom in (standard/thorough):** Select sections that need more detail and expand them with deeper context: commands, file paths, error messages, alternatives, and why they matter.
   - **Pass 4 — Deep zoom (thorough):** For the same sections, add another layer: full reasoning, failed attempts, edge cases, and exact state.
   - **Pass 5 — Anchor and readiness:** Ensure the first section fully captures the session's origin, goal, and scope. Ensure the last section fully captures the current state, next action, blockers, and tools in focus. Ask whether a fresh session could continue from this handoff without reading the linked artifacts. If not, note the gaps explicitly.
5. **Remove duplicate links and tighten the snapshot.** Ensure the next session can act without reading every linked artifact.
6. **Write the snapshot and report the path.** Write the populated snapshot to the resolved path and return the absolute path.

## Section selection for zoom-in passes

A section needs more detail when any of these are true:

- It contains a blocker or unresolved question.
- It contains a decision that affects future work.
- It is referenced by the next action.
- It involves complex technical context (multiple files, tools, or concepts).
- The user expressed strong preferences or constraints there.
- It would be hard for a fresh session to understand from the earlier passes.

## Timeline segmentation

A new timeline section starts when any of these happen:

- The user changes direction or scope.
- A significant subtask is completed.
- New information is discovered that changes the plan.
- A subagent or major tool is used.
- The user makes a decision or commitment.
- There is a clear pause or context switch.

## Output

- With key: `{context_dir}/handoff/{normalized-key}.md`
- Without key: `{context_dir}/handoff/unticketed.md`

Keys are normalized to lowercase letters, digits, and hyphens for use as file names. For example, `ABC-123` becomes `abc-123`.

## Security

- The skill writes only new files. It archives but never deletes or overwrites existing handoffs.
- The user's explicit invocation of `handoff` is the approval to write the new snapshot.
- No secrets are written to config files during initialization.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).
