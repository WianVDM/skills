# Checkpoint Manager

Follow the `worker-contract` return contract. Reads the current `state.md` and report document, updates the phase checklist and current focus, and returns a concise status summary.

## In scope

- Read `{context_dir}/pr-report/{key}/state.md` and `{context_dir}/pr-report/{key}-report.md`.
- Infer completed, in-progress, and pending phases from `<!-- STATUS: completed -->` markers and the state checklist.
- Update `## Phase Checklist`, `## Current Focus`, and `## Last Completed Action`.
- Return a concise status summary with completed sections, pending sections, and the next recommended action.

## Out of scope

- Fetching PR, CI, or review data.
- Forming triage or synthesis decisions.
- Writing report content unless explicitly authorized as the report writer.

## Inputs

- PR key
- Path to state file
- Path to report document
- What just happened (e.g., "the PR source adapter returned normalized threads")
- Optional: specific question, e.g., "where were we after compaction?"

## Outputs

Return the standard worker contract with `status` and any updated artifact paths. Include:

- Phase status table
- Completed report sections
- Pending report sections
- Current focus
- Last completed action

## Rules

- Infer completion from `<!-- STATUS: completed -->` markers.
- Be conservative: only mark a phase complete when evidence exists.
- After compaction, report exact state without assumption.
- Escalate to `needs_input` with the exact question and options if user input is required.
