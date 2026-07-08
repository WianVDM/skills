# PR Report Workflow

This is the detailed step sequence that the `pr-report` skill follows. It is a concrete breakdown of the high-level phases described in `SKILL.md`.

## Step-by-step sequence

1. **Load config and state** — read `{config_dir}/pr-report.yaml`, `{config_dir}/shared.yaml`, and `{context_dir}/pr-report/{key}/state.md` if they exist. `{config_dir}` and `{context_dir}` are discovered by `detect-project-context`.
2. **Resolve PR** — identify PR number, repo, branch, and ticket key if any.
3. **Detect adapters** — identify available PR source, CI, static-analysis, issue-tracker, and notification adapters. See [CAPABILITIES.md](CAPABILITIES.md) and [ADAPTER_ARCHITECTURE.md](ADAPTER_ARCHITECTURE.md).
4. **Create skeleton report** — write `{context_dir}/pr-report/{key}-report.md` with section headers and status markers. See [CHECKPOINTING.md](CHECKPOINTING.md).
5. **Fetch PR metadata and changed files** — delegate to the configured `pr-source` adapter.
6. **Update report and checkpoint** — write results into the report and ask `checkpoint-manager` to update phase state.
7. **Fetch review threads and comments** — delegate to the configured `pr-source` adapter. Normalize inline threads, top-level reviews, and rebuttals.
8. **Update report and checkpoint**.
9. **Fetch static analysis** — delegate to the configured `static-analysis-source` adapter.
10. **Update report and checkpoint**.
11. **Fetch CI / build status** — delegate to the configured `ci-source` adapter. Include required checks and failing job log summaries.
12. **Update report and checkpoint**.
13. **Fetch issue tracker scope** — delegate to the configured `issue-tracker-source` adapter, if available.
14. **Update report and checkpoint**.
15. **Fetch notification feedback** — delegate to configured `notification-source` adapters, if any.
16. **Update report and checkpoint**.
17. **Context scan** — delegate to `context-scout` for reports related to the ticket/issue key.
18. **Update report and checkpoint**.
19. **Scope check** — delegate to `scope-checker`. Compare feedback to the ticket or PR description.
20. **Update report and checkpoint**.
21. **Triage and synthesize issues** — delegate to `issue-synthesizer`. Group duplicates, challenge every comment, apply source weighting, and produce the issue board.
22. **Update report and checkpoint**.
23. **Render final report** — delegate to `report-writer` to finalize pending Markdown sections.
24. **Optional HTML dashboard** — delegate to `html-renderer` or render the template asset.
25. **Final validation** — ask `checkpoint-manager` to verify all phases are complete and consistent.
26. **Present findings** — give the user a concise summary with open issues (including a brief issue list or board summary), CI status, and suggested next step.
