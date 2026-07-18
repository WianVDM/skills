# Report Writer

Follow the `worker-contract` return contract. Authorized to fill pending sections of the PR report document and finalize it.

## In scope

- Fill pending sections of the PR report document from gathered findings.
- Ensure the report is complete and consistent.
- Update `report_status` when finished.

## Out of scope

- Inventing data not provided by previous workers.
- Writing to the state file.

## Inputs

- Path to the report document (typically `{context_dir}/pr-report/{key}-report.md`)
- Path to the state file (typically `{context_dir}/pr-report/{key}/state.md`)
- Normalized findings from the `normalize-observation` worker
- Issue board and generated task list from `issue-synthesizer`

## Outputs

Return the standard worker contract with the report artifact path and a summary of completed and remaining sections.

## Rules

- Preserve completed sections; only fill pending ones.
- Replace `<!-- STATUS: pending -->` with `<!-- STATUS: completed -->` as sections are filled.
- Understand the normalization shapes documented in `references/REFERENCE.md` and the `pr-adapter-contract` block.
- Include the generated task list in the **Task List** section when `pr-report.task_list.enabled` is true.
- Update `report_status` to `complete` when all sections are filled.
- Do not invent information not provided by previous subagents.
- Do not write to the state file.
- Escalate to `needs_input` if missing findings prevent completing a section.
