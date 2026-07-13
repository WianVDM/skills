---
name: debrief
description: "Debrief a ticket before implementation. Use when the user asks to 'understand a ticket', 'debrief a ticket', 'scope this ticket', or 'what does this ticket need'."
invocation: model-invoked
depends:
  - checkpoint
  - research-ticket
  - map-ticket-relationships
  - explore-code
  - challenge-assumptions
  - scan-context
  - context-reports
  - worker-contract
  - detect-project-context
  - baseline
  - parse-skill-frontmatter
  - token-resolver
---

# debrief

## Purpose

Produce a structured, confidence-rated understanding of **one ticket** before implementation.

## Scope

### In scope

- Resolve a single ticket key from user input, branch, previous state, or explicit ask.
- Gather ticket data, relationships, codebase evidence, and related context reports.
- Form and challenge explicit assumptions.
- Calculate confidence and identify gaps.
- Write a structured debrief report and maintain resume state.
- Present a concise summary to the user.

### Out of scope

- **Handle multiple tickets in one invocation.** Debrief exactly one ticket per run.
- **Implement, test, or modify code.** This is investigation only.
- **Recommend the next skill.** `debrief` ends with a report, not a plan.
- **Decide execution order.** It produces understanding, not a task sequence.
- **Ask the user questions** except when a required input is missing or confidence is Red.

## Initialization

`debrief` is a global, configurable skill. Before it can debrief a ticket, it must detect the project environment and ensure the project-level config file exists.

**When initialization runs:**

- On first run in a project, when `{config_dir}/debrief.yaml` is missing.
- When the user asks to reconfigure the skill.
- When the existing config is missing required keys or uses an older schema.

**What initialization does:**

1. Detect project context (`detect-project-context`).
2. Load the skill-level defaults from `config.yaml`.
3. Check for `{config_dir}/debrief.yaml`.
4. If the file is missing, propose the default config to the user.
5. If the file exists but uses an older schema, migrate it to the current schema.
6. Ask the user for any required values that cannot be detected or defaulted.
7. Validate required capabilities.
8. Write the config and initial notes only after explicit approval.
9. Report readiness.

**Idempotency:** running initialization twice must not overwrite user edits or create duplicate files. If the config is already present and current, the skill reports that it is initialized and proceeds.

**Implementation:** the initialization phase is implemented by `scripts/initialize.py`. The conductor invokes it with the detected `marker_dir` and only passes `--approve` after the user confirms.

## Branches

| Branch | Trigger | Outcome |
|---|---|---|
| **initialize** | No project config exists, the config is incomplete, or the user asks to reconfigure. | Detect the environment, create or migrate config, validate required capabilities, and report readiness. |
| **new** | No existing state for this ticket, or the user explicitly asks for a fresh debrief. | Run the full 5-phase workflow. |
| **resume** | A `checkpoint` state file exists for this ticket and is fresh. | Resume from the last completed phase. |
| **manual** | The tracker is `manual` or credentials are missing. | Ask the user for ticket context and continue. |
| **blocked** | A required capability is missing. | Stop and report the blocker. |

## Workflow

Each phase ends by updating `checkpoint` state. The conductor always records the current focus and the last completed action.

### Phase 0 — Bootstrap and resume

**Completion criterion:** Project context is detected, initialization is complete, config is loaded, the ticket key is resolved, tracker credentials are resolved, and `checkpoint` state is created or resumed.

Steps:

1. Detect project context (`detect-project-context`).
2. Run initialization if needed. If `{config_dir}/debrief.yaml` is missing or incomplete, invoke `scripts/initialize.py` and ask the user for approval before writing. Then load config (`load-skill-config`) with the defaults from `references/CONFIG_PATTERN.md`.
3. Detect the issue tracker (`detect-issue-tracker`) if `issue_tracker: auto`; pass `config_dir` from `detect-project-context` as input. If `issue_tracker` is not `auto`, validate the configured tracker.
4. Extract the ticket key (`extract-ticket-key`) from user input, branch, or previous state.
5. Get git state (`get-git-state`) if needed.
6. Resolve tracker credentials (`token-resolver`). The conductor builds a `token_config` from the tracker block in `debrief.yaml` (e.g. `env_var`, `mcp_config_sources`, `mcp_server_key`) and invokes `token-resolver`. If the token is missing and prompting is not authorized, report `blocked` and stop.
7. Create or resume checkpoint (`checkpoint`) at `{context_dir}/debrief/{key}/state.md`.
8. Check whether an existing debrief report is fresh (`check-debrief-freshness`). If a report exists, parse its frontmatter with `parse-skill-frontmatter` and pass it to the script. If the report is fresh and the user has not asked for a fresh debrief, enter the `resume` branch.
9. If any required capability is missing, report `blocked` and stop.

### Phase 1 — Gather evidence

**Completion criterion:** `research-ticket` has returned, `map-ticket-relationships` has returned, related context reports are discovered, and `baseline` has run or been skipped with a recorded reason.

Steps:

1. Research the ticket (`research-ticket`).
2. Map relationships (`map-ticket-relationships`).
3. Explore code (`explore-code`) only if the task type is `code`/`ui` or a code-related ambiguity exists.
4. Scan context (`scan-context`) for related baseline reports, handoffs, or prior debriefs.
5. Detect verifiable state (`detect-verifiable-state`).
6. Run `baseline` according to `baseline_mode`:
   - If `baseline_mode` is `skip`, record the skip reason and do not run `baseline`.
   - If `baseline_mode` is `required` and `detect-verifiable-state` returns `verifiable: false`, stop and ask the user for the observable state or the acceptance criteria that make the ticket verifiable. Record the user's response in `checkpoint`.
   - If `baseline_mode` is `required` or `optional` and `detect-verifiable-state` returns `verifiable: true`, run `baseline`. If `baseline` returns `needs_input`, surface the question to the user and record the response in `checkpoint`.
   - If `baseline_mode` is `optional` and `detect-verifiable-state` returns `verifiable: false`, record the skip reason and continue.
7. Update `checkpoint`.

### Phase 2 — Form and challenge assumptions

**Completion criterion:** Assumptions are formed, challenged, confidence is calculated, and any Red-confidence blockers are either resolved by the user or recorded as unresolved.

Steps:

1. Identify ambiguities from the gathered evidence.
2. Form explicit assumptions (`form-assumptions` subagent). The subagent returns a worker-contract result; the conductor extracts the `assumptions` object from the `## Findings` section.
3. Challenge assumptions (`challenge-assumptions`).
4. Calculate confidence (`calculate-confidence`).
5. If confidence is Red (below the threshold), produce a blocker report and ask the user to resolve the blockers. Record overrides in `checkpoint`.
6. Loop back to evidence gathering only if the user provides new information, up to `max_resolution_loops` times.
7. Update `checkpoint`.

### Phase 3 — Synthesize

**Completion criterion:** The debrief report is written to `{context_dir}/debrief/{key}-{slug}.md` and `checkpoint` marks the synthesize phase complete.

Steps:

1. Synthesize the final report (`synthesis-writer` subagent) from all evidence, assumptions, and confidence. The subagent returns a worker-contract result; the conductor extracts the written `report_path` from the `artifacts` frontmatter and the summary from the `## Summary` section.
2. Check whether `{context_dir}/debrief/{key}-{slug}.md` already exists. If it does, confirm with the user before overwriting and record the decision in `checkpoint`. If the user declines, append a suffix or choose a new slug and confirm again.
3. Write the report incrementally: update the report file after each phase so that context compaction does not lose progress.
4. Finalize the report at the canonical path.
5. Update `checkpoint`.

### Phase 4 — Present

**Completion criterion:** A concise summary is delivered to the user and the final `checkpoint` state is recorded.

Steps:

1. Present the ticket, confidence level, key assumptions, confidence gaps, and report path.
2. Record final state in `checkpoint`.

## State and report paths

```text
{context_dir}/
├── debrief/
│   ├── {key}-{slug}.md      # canonical debrief report
│   └── {key}/
│       └── state.md          # checkpoint state
```

## Dependencies

See `references/DEPENDENCIES.md` for the full dependency surface.

## Configuration

See `references/CONFIG_PATTERN.md` for the `debrief.yaml` schema and defaults.

## Subagents

- `subagents/form-assumptions.md` — turns ambiguities into explicit assumptions.
- `subagents/synthesis-writer.md` — writes the final debrief report from evidence and state.

## Lazy dependency evaluation

Required dependencies are validated eagerly during initialization and Phase 0. Recommended and optional dependencies are evaluated lazily, only when the branch or method that needs them is selected.

| Dependency | Category | Evaluation | Loading trigger |
|---|---|---|---|
| `checkpoint` | Required | Eager | Always loaded before any workflow phase. |
| `research-ticket` | Required | Eager | Always loaded in Phase 1. |
| `challenge-assumptions` | Required | Eager | Always loaded in Phase 2. |
| `context-reports` | Required | Eager | Used for report schemas and freshness conventions in every phase. |
| `worker-contract` | Required | Eager | Subagents use this contract in every phase that delegates work. |
| `detect-project-context` | Required | Eager | Used during initialization and Phase 0. |
| `map-ticket-relationships` | Recommended | Lazy | Loaded in Phase 1 when the tracker provides relationship data or the user asks for it. If missing, the conductor performs minimal inline mapping and records the degraded depth. |
| `explore-code` | Recommended | Lazy | Loaded in Phase 1 when the task type is `code`/`ui` or a code-related ambiguity exists. If missing, the conductor skips code exploration and records the gap. |
| `scan-context` | Recommended | Lazy | Loaded in Phase 1 when the conductor wants to discover related reports. If missing, the conductor proceeds without prior context and notes the gap. |
| `baseline` | Recommended | Lazy | Loaded in Phase 1 only when `detect-verifiable-state` returns `verifiable: true` and `baseline_mode != skip`. If missing, the conductor asks the user to describe observable state and records the response. |

**Degradation disclosure:** when a recommended dependency is missing and the conductor uses a fallback, it tells the user which skill was unavailable, what fallback is being used, and records the choice in `checkpoint`.

## Security

- No secrets are stored in skill files or config.
- Tracker tokens are referenced by env var name, not value.
- Confirm before overwriting an existing debrief report.
- Fail closed when a required capability is missing.
- Prefer read-only inspection in untrusted projects; ask before writing.

## Evaluation

- Trigger evals: `evals/evals.json`.
- Composition tests: verify the conductor invokes the correct building blocks in the correct order.
- Pressure tests: missing credentials, stale reports, Red-confidence loops, and manual tracker fallback.
