# Validation

Before considering the skill complete or using it in a real run:

## Frontmatter

- [ ] `name` is lowercase with hyphens and matches the directory name.
- [ ] `description` is under 1024 characters and includes triggers.
- [ ] `version`, `invocation`, and `depends` are present.

## SKILL.md

- [ ] Focuses on intent and guidelines, not exact commands.
- [ ] Declares skill type (workflow/conductor).
- [ ] Lists out-of-scope behavior.
- [ ] Documents capability-first tool discovery and manual fallback.
- [ ] Documents focused mode (`/pr-report ci`, `/pr-report reviews`, etc.).
- [ ] Documents progress reporting during the collect phase.
- [ ] Links to all reference files.

## Config

- [ ] `config.yaml` exists next to `SKILL.md` and declares shared and skill-specific keys.
- [ ] `requires_setup: true` is declared.
- [ ] Config uses provider names (`pr-report.tools.{capability}.provider`) not adapter names.
- [ ] New shared keys are registered in `docs/skill-standards/reference/config-keys.md`.

## References

- [ ] All linked reference files exist.
- [ ] `TOOL_SELECTION.md` documents capability-to-tool mapping, tool categories, discovery rules, selection hierarchy, conflict resolution, timeout/retry policy, direct API call policy, degradation behavior, and provider capability matrix.
- [ ] `CONFIG_PATTERN.md` documents detect/ask/persist/reuse using `{config_dir}` and `{context_dir}` discovered by `detect-project-context`.
- [ ] `CONFIG_PATTERN.md` does not hardcode harness names or tool paths.
- [ ] `CONTEXT_REPORTS.md` documents output schemas and locations using `{context_dir}`.
- [ ] `CONTEXT_REPORTS.md` documents generic context scanning, relevance from frontmatter, and fallback behavior.
- [ ] `COMMENT_TRIAGE.md` documents source weighting and challenge rules.
- [ ] `CHECKPOINTING.md` documents phases, resume rules, and state validation/recovery rules.
- [ ] `REFERENCE.md` documents skill version vs report/state schema version and migration strategy.
- [ ] `VERSIONING.md` documents the versioning policy and the old-to-new config migration path.
- [ ] `DEPENDENCIES.md` lists only cross-cutting building blocks as required skill dependencies.

## Subagents

- [ ] Each subagent has a narrow scope.
- [ ] Each subagent references the `worker-contract` skill.
- [ ] Each worker returns `status`, `artifacts`, `summary`, `findings`, `decisions made`, `open questions`, and `blockers` as defined by the standard contract.
- [ ] Subagents do not write directly to the report, except for the explicitly authorized report writer.
- [ ] `normalize-{pr,ci,static-analysis,issue-tracker}` subagents exist and define their input/output contracts.
- [ ] `context-scout` accepts `{context_dir}` as an input rather than hardcoding a path.

## Dependencies

- [ ] Required skills are declared in `references/DEPENDENCIES.md` or `SKILL.md` frontmatter.
- [ ] `token-resolver` and `detect-project-context` are declared.
- [ ] Consumed context reports are declared.
- [ ] Required external tools, APIs, MCP servers, and env vars are documented.
- [ ] Absence of an optional dependency is handled gracefully.

## Security

- [ ] No secrets are hardcoded.
- [ ] Tokens are referenced by env var names or extracted from MCP config by `token-resolver`.
- [ ] Tokens are not logged in report or state files.
- [ ] Direct API calls require explicit user-configured endpoint and confirmation.

## Scenarios to walk through

1. First run with no config — skill asks for missing values and persists them.
2. Second run on the same PR — skill reads state and reports deltas.
3. PR with only bot comments — skill challenges and downgrades appropriately.
4. PR with failing CI — skill surfaces blocker and summarizes logs.
5. Context compaction mid-run — skill resumes from the pending phase.
6. No configured PR tool — skill falls back to manual user input and still produces a report.
7. Missing CI/static-analysis/issue-tracker — skill reports plainly and continues.
8. Better tool available than current source — skill discloses the better tool and asks before accepting degraded data.
9. Degraded source accepted — skill records the degraded source and the better alternative in the Data sources section.
10. Conflicting tools disagree on a blocker — skill records conflict and asks the user which source to trust.
11. Corrupted state file — skill archives state and starts fresh.
12. Focused mode (`/pr-report ci`) — skill collects only the requested capability.
