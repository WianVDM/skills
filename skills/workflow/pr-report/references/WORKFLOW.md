# PR Report Workflow

This is the detailed step sequence that the `pr-report` skill follows. It is a concrete breakdown of the high-level phases described in `SKILL.md`.

## Step-by-step sequence

1. **Load config and state** — read `.agents/config/pr-report.yaml` and `.agents/context/pr-report/{key}/state.md` if they exist.
2. **Resolve PR** — identify PR number, repo, branch, and ticket key if any.
3. **Detect capabilities** — identify available PR platform, static-analysis, issue-tracker, and CI providers. See [CAPABILITIES.md](CAPABILITIES.md).
4. **Create skeleton report** — write `.agents/context/pr-report/{key}-report.md` with section headers and status markers. See [CHECKPOINTING.md](CHECKPOINTING.md).
5. **Fetch PR metadata and changed files** — delegate to `pr-researcher`.
6. **Update report and checkpoint** — write results into the report and ask `checkpoint-manager` to update phase state.
7. **Fetch review threads and comments** — delegate to `thread-analyzer`. Normalize inline threads, top-level reviews, and rebuttals.
8. **Update report and checkpoint**.
9. **Fetch static analysis** — delegate to `static-analysis-fetcher`.
10. **Update report and checkpoint**.
11. **Fetch CI / build status** — delegate to `ci-status-fetcher`. Include required checks and failing job log summaries.
12. **Update report and checkpoint**.
13. **Scope check** — delegate to `scope-checker`. Compare feedback to the ticket or PR description.
14. **Update report and checkpoint**.
15. **Triage and synthesize issues** — delegate to `issue-synthesizer`. Group duplicates, challenge every comment, apply source weighting, and produce the issue board.
16. **Update report and checkpoint**.
17. **Render final report** — delegate to `report-writer` to finalize pending Markdown sections.
18. **Optional HTML dashboard** — delegate to `html-renderer` to produce the human-facing variant.
19. **Final validation** — ask `checkpoint-manager` to verify all phases are complete and consistent.
20. **Present findings** — give the user a concise summary with open issues (including a brief issue list or board summary), CI status, and suggested next step.
