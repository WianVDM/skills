# Workflow

This document describes the conductor flow and subagent orchestration for the `verify-branch` skill. It is written for implementers and maintainers who need to understand how the main skill delegates work, handles interruptions, and arrives at a verdict.

The skill is a thin conductor. It loads state, detects the verification target, consults the user when config is missing, delegates each gate to a focused subagent, aggregates results, and delegates final reporting. Heavy lifting lives in subagents and scripts; the main skill owns sequencing, user consultation, and the final verdict.

## Conductor flow overview

A verification run has six phases:

| Phase | Name | Purpose | Delegates to |
|-------|------|---------|--------------|
| 1 | Setup | Load config/state, detect branch and diff, scan context | `context-scout` |
| 2 | Resolve config | Ensure every enabled gate has enough config to run | `bootstrap` |
| 3 | Plan execution | Filter and order gates by mode, tags, and dependencies | `scripts/lib/plan-execution.js` |
| 4 | Execute gates | Run each planned gate in order | gate subagents (see dispatch table) |
| 5 | Aggregate | Compute the overall PASS/FAIL verdict using `verdict_policy` | main skill |
| 6 | Report | Write the verification report and update state | `report-writer`, `checkpoint` block |

The main skill never runs project commands, tests, or static analysis directly. It delegates those tasks to subagents and only combines the returned statuses.

## Gate dispatch

Each gate is dispatched to a subagent based on its `type`:

| Gate `type` | Subagent | Purpose |
|-------------|----------|---------|
| `command` | `test-gate` | Run one or more shell commands. |
| `mapper` | `spec-coverage-gate` | Map changed source files to expected spec files. |
| `standards` | `standards-gate` | Apply rules from configured standards sources. |
| `custom` | `custom-gate` | Run a single adapter through `scripts/run-gate.js`. |
| `static-analysis` (legacy v3) | `static-analysis-gate` | Run legacy sub-gates. |

The gate registry is open. Any gate name can be added under `preferences.gates` with a valid `type` and the required config.

## Phase 1: Setup

1. **Determine the project root.** All paths are resolved relative to the project root.
2. **Load shared config.** Read `.agents/config/shared.yaml` if it exists.
3. **Load skill config.** Read `.agents/config/verify-branch.yaml` if it exists. A missing config file is not a hard stop; the run proceeds to Phase 2.
4. **Load resume state.** If `.agents/context/verify-branch/{branch-name}-state.md` exists, read it. If it contains completed gates, skip those gates in Phase 4.
5. **Detect current branch.** Use `git branch --show-current` or the branch provided by the user.
6. **Detect default branch.** Use `git rev-parse --abbrev-ref origin/HEAD` unless `preferences.default_branch` overrides it. If detection fails and no override exists, stop and ask the user.
7. **Detect base ref.** Use `preferences.base_ref` if set; otherwise use the default branch.
8. **Compute changed files.** Diff the current branch against the base ref. Include staged, unstaged, untracked, and committed-but-unmerged changes based on `preferences.include_uncommitted`.
9. **Scan context.** Delegate to `context-scout` with:
   - `current_branch`
   - `current_commit`
   - `ticket_key` (inferred from branch name if possible)
   - `max_age_threshold` from config or default
   - `cwd` (project root)

The scout returns `fresh_matches` and `stale_matches`. Fresh matches may be passed to gate subagents as advisory context. Stale matches are noted in the final report and ignored for decision-making.

**Hard stops in Phase 1:**

- Not inside a git repository.
- Default branch cannot be detected and no override is provided.
- Context scout returns `blocked` because `.agents/context/` is unreadable. (The skill may proceed without context.)

## Phase 2: Resolve config

1. **Validate loaded config.** For each gate under `preferences.gates`, check whether it is enabled and whether required values are present.
2. **Skip disabled gates.** Gates with `enabled: false` are recorded as `SKIPPED` for bookkeeping, but a disabled required gate is treated as `NOT_APPLICABLE` when the verdict is computed.
3. **Run auto-detection for `enabled: auto` gates.** Use the detection scripts to determine whether a tool is available. `auto` means "run if a tool is available, otherwise treat as optional."
4. **Run bootstrap if config is missing.** If the config file is missing, or if a required gate has no command, mapping, or source, delegate to the `bootstrap` subagent. The subagent proposes a config and returns `status: needs_input` if the user must confirm or provide values.
5. **Ask the user on-the-fly for missing values.** If a specific value is missing during execution, pause, ask, persist the answer, and resume. See [Config on-the-fly rules](#config-on-the-fly-rules) below.
6. **Record resolved config in state.** Before moving to Phase 3, record the resolved gate checklist in the state file via `checkpoint/update`.

**Hard stops in Phase 2:**

- A required gate has no available tool and the user declines to provide one or skip it.
- The bootstrap subagent returns `blocked` because the project root is inaccessible or not a git repo.

## Phase 3: Plan execution

Before running gates, the skill builds an execution plan from the resolved config:

1. **Filter by mode.** `preferences.execution_mode` controls which gates are included:
   - `full` — all enabled gates.
   - `quick` — required gates plus gates tagged `fast` or `quick`.
   - `security-audit` — only gates tagged `security`.
2. **Filter by tags.** If `preferences.tags` is set, only gates that have all listed tags are included.
3. **Filter disabled gates.** Gates with `enabled: false` are recorded as `SKIPPED` for bookkeeping; disabled required gates are treated as `NOT_APPLICABLE` at verdict time.
4. **Order by dependencies.** Gates with `depends_on` are sorted so dependencies run first. Cycles and missing dependencies are reported as planning errors.
5. **Dry run.** If `preferences.dry_run` is `true`, the skill reports the planned gates and stops without executing them.

The plan is produced by `scripts/lib/plan-execution.js`. Planning errors do not fail the overall verdict unless a required gate cannot be scheduled.

## Phase 4: Execute gates

Run gates in the order below. The default `max_concurrent_gates: 1` means gates run sequentially. Parallel execution is allowed only when the config raises the limit and the gate subagents do not contend for the same resources or files.

### Gate order

1. `test` — delegate to `test-gate`
2. `spec-coverage` — delegate to `spec-coverage-gate`
3. `standards` — delegate to `standards-gate`
4. `static-analysis` — delegate to `static-analysis-gate`, which internally runs its sub-gates
5. `security-audit` — optional command gate, delegate to `test-gate` or run as a custom command
6. `style-format` — optional command gate, delegate to `test-gate` or run as a custom command

Each subagent receives:

- The list of changed files.
- The resolved gate configuration.
- The `fail_fast` flag for that gate.
- Fresh context reports (advisory only).

Each subagent returns a standard worker contract (see [references/WORKER_CONTRACT.md](WORKER_CONTRACT.md)) with `status`, `artifacts`, and a `gate_result` containing:

- `gate`: the gate name
- `status`: `PASS`, `FAIL`, `ERROR`, `NOT_APPLICABLE`, or `SKIPPED`
- `adapter`: the adapter or command used
- `findings`: list of findings with file, line, rule, severity, message, and introduced flag
- `summary`: human-readable summary
- `raw_output`: optional command output

### Handling `needs_input` and `blocked` from a gate subagent

- If a subagent returns `needs_input`, the main skill stops the gate sequence, asks the user the exact question provided by the subagent, persists the answer, and resumes the same gate.
- If a subagent returns `blocked`, the gate is marked `ERROR` if required or `SKIPPED` if optional. The skill continues to the next gate unless the blocked gate is required and the user declines to proceed.
- If a subagent returns `partial`, the main skill treats the result as the best available outcome and continues.

### Sequential execution rule

Gates run one at a time unless the user explicitly configures `max_concurrent_gates > 1`. The order is fixed because later gates may consume earlier results (for example, the static-analysis gate may skip sub-gates already covered by the test gate). If a gate is promoted to `required` and `fail_fast: true` is set at the skill level, the skill stops after the first required gate failure.

### Checkpointing after each gate

After each gate returns, the main skill invokes `checkpoint/update` to:

- Mark the gate as complete in the state file.
- Append the gate result to the collected results.
- Update `Current Focus` and `Next Action`.

This allows the run to resume from the next pending gate after an interruption.

## Phase 5: Aggregate

The main skill computes the overall verdict from the collected gate results.

1. Separate gates by `importance`:
   - `required` gates influence the verdict.
   - `optional` gates are reported but do not influence the verdict.
2. Count required gates that returned `PASS`.
3. Count required gates that returned `FAIL`, `ERROR`, or `SKIPPED` when a required gate should have run.
4. Determine the verdict:
   - `PASS` if every required gate returned `PASS` or `NOT_APPLICABLE`.
   - `FAIL` if any required gate returned `FAIL`, `ERROR`, or was skipped when it should have run.
5. Count optional gate results separately for reporting.
6. Do not let optional findings, stale context reports, or fresh advisory reports change the verdict.

The verdict is computed by the main skill, not delegated, because it is a simple rule over the collected results.

## Phase 6: Report

1. **Delegate report writing to `report-writer`.** Pass:
   - `branch`, `base`, `commit`, `generated_at`
   - All gate results
   - `fresh_matches` and `stale_matches` from the context scout
   - The computed verdict and counts
2. **The report writer writes** `.agents/context/verify-branch/{branch-name}.md` using the report template.
3. **Finalize state via `checkpoint/update`.** Write or update `.agents/context/verify-branch/{branch-name}-state.md` with:
   - All gates marked complete
   - The final verdict
   - A `Next Action` of `complete` or `user review required`
4. **Present the verdict to the user.** The skill returns a concise summary with the verdict, the list of failed gates, and a link to the report.

## Resume behavior

If the main skill is resumed after an interruption or context compaction, it follows these rules:

1. **Read the state file** `.agents/context/verify-branch/{branch-name}-state.md`.
2. **Read the report file** if it exists, to recover already-recorded results.
3. **Invoke `checkpoint/resume`** to get the current status, completed gates, pending gates, and the next pending gate.
4. **Handle a corrupted state file.** If the state file exists but cannot be parsed, the main skill discards it and treats the run as a fresh verification. It restarts from Phase 1, re-detecting the branch, diff, and context.
5. **Verify git state matches.** If the current branch or commit has changed since the state file was written, the skill warns the user and may restart the run from Phase 1.
6. **Resume from the first pending gate.** Do not re-run completed gates unless the user explicitly asks or the git state has changed.
7. **Re-read config before the next gate.** If the user updated config during the interruption, the new values apply to pending gates only.

The checkpoint manager is called in two situations:

- After every subagent returns, to record progress.
- After a context compaction or interruption, to report current status and the next action.

## Gate execution rules

| Situation | Action |
|-----------|--------|
| Required gate, tool available | Run it. Result contributes to the verdict. |
| Required gate, no tool available | Consult the user. If the user provides a tool or command, run it. If the user declines, mark `ERROR` and overall verdict is `FAIL`. |
| Optional gate, no tool available | Mark `SKIPPED` with a note. Continue. |
| Required gate returns `FAIL` or `ERROR` | Overall verdict is `FAIL`. Continue running remaining gates unless `fail_fast: true`. |
| Optional gate returns `FAIL` or `ERROR` | Report it. Do not change the overall verdict. |
| Gate returns `NOT_APPLICABLE` | Treat as `PASS` for verdict purposes. |
| Gate returns `SKIPPED` and is required | Treat as `ERROR` for verdict purposes, unless the gate was explicitly disabled (`enabled: false`), in which case treat it as `NOT_APPLICABLE`. |
| Gate returns `SKIPPED` and is optional | Accept and continue. |
| `fail_fast` is `true` and a required gate fails | Stop after the current gate. Finalize the report with the gates that ran. |
| `fail_fast` is `false` | Run all gates and collect all results. |

## Config on-the-fly rules

Missing config values are resolved during execution, not before.

1. The skill detects that a gate is enabled but a required value is missing (for example, a `command`, `source_pattern`, or `path`).
2. The skill pauses the current gate.
3. It asks the user for the missing value, explaining why it is needed and pre-populating with any detected default.
4. It writes the value to `.agents/config/verify-branch.yaml`.
5. It resumes the gate using the updated config.
6. If the user declines:
   - A required gate is marked `ERROR`.
   - An optional gate is marked `SKIPPED`.
7. If the user updates config manually during a run, the skill completes the current gate with the original config, then re-reads config before the next gate.
8. All config changes are recorded in the report notes and checkpoint state.

## Error handling

Subagent returns follow the standard worker contract: `status` can be `complete`, `partial`, `needs_input`, or `blocked`. The main skill maps these to gate results and overall behavior as follows:

| Subagent status | Gate result | Main skill action |
|-----------------|-------------|-------------------|
| `complete` | Use the `gate_result.status` returned. | Continue to the next gate. |
| `partial` | Use the returned `gate_result.status`; if none, mark `ERROR`. | Continue to the next gate but note the partial result. |
| `needs_input` | Gate is paused. | Ask the user and resume the same gate. |
| `blocked` | `ERROR` if required, `SKIPPED` if optional. | Continue unless the user declines to resolve a required gate. |
| Missing `gate_result` | `ERROR`. | Continue and report the missing result. |

Tool failures inside a gate (non-zero exit, timeout, adapter crash) are reported by the gate subagent as `FAIL` or `ERROR` and handled according to the gate execution rules table.

If the report writer or checkpoint manager returns `blocked`, the main skill reports the final verdict to the user and explains that the report could not be written. The gate results are still valid and are presented directly.

## Cross-skill context rules

The skill consumes reports from `.agents/context/` generically. It does not depend on reports from any specific skill.

- **Fresh reports** may be passed to gate subagents as background context. They are advisory only.
- **Stale reports** are noted in the final report and ignored for decision-making.
- A report is stale if its `branch`, `commit`, or `generated_at` does not match the current verification target.
- Reports whose `skill` frontmatter field is `verify-branch` are ignored to avoid circular self-reference.
- No report from another skill may change the verdict. Even if a baseline report says a bug is reproduced, the test gate must still run to produce the current verdict.
- If a gate subagent can use a fresh report to avoid redundant work (for example, skipping a test that another skill already ran), it must still return a result that is valid for the current branch state.
