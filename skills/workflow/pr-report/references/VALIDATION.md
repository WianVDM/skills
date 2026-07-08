# Validation

Before considering the skill complete or using it in a real run:

## Frontmatter

- [ ] `name` is lowercase with hyphens and matches the directory name.
- [ ] `description` is under 1024 characters and includes triggers.
- [ ] `license`, `invocation`, and `metadata` are present.

## SKILL.md

- [ ] Focuses on intent and guidelines, not exact commands.
- [ ] Declares skill type (workflow/conductor).
- [ ] Lists out-of-scope behavior.
- [ ] Documents lazy dependency evaluation and first-run behavior via a pointer to `references/CONFIG_PATTERN.md`.
- [ ] Links to all reference files.

## Config

- [ ] `config.yaml` exists next to `SKILL.md` and declares shared and skill-specific keys.
- [ ] `requires_setup: true` is declared.
- [ ] New shared keys are registered in `docs/skill-standards/CONFIG_KEYS.md`.

## References

- [ ] All linked reference files exist.
- [ ] `ADAPTER_ARCHITECTURE.md` documents the adapter taxonomy and discovery model; the detailed interface contract lives in the `pr-adapter-contract` building block.
- [ ] `ADAPTER_REGISTRY.md` documents the default registry and how to override it.
- [ ] `CONFIG_PATTERN.md` documents detect/ask/persist/reuse using `{config_dir}` and `{context_dir}` discovered by `detect-project-context`.
- [ ] `CONFIG_PATTERN.md` does not hardcode harness names or tool paths.
- [ ] `CONTEXT_REPORTS.md` documents output schemas and locations using `{context_dir}`.
- [ ] `CONTEXT_REPORTS.md` documents generic context scanning, relevance from frontmatter, and fallback behavior.
- [ ] `CAPABILITIES.md` documents adapter discovery and lazy loading.
- [ ] `COMMENT_TRIAGE.md` documents source weighting and challenge rules.
- [ ] `CHECKPOINTING.md` documents phases and resume rules.
- [ ] `REFERENCE.md` documents skill version vs report/state schema version and migration strategy.
- [ ] `VERSIONING.md` documents the versioning policy.

## Subagents

- [ ] Each subagent has a narrow scope.
- [ ] Each subagent references the `worker-contract` skill.
- [ ] Each worker returns `status`, `artifacts`, `summary`, `findings`, `decisions made`, `open questions`, and `blockers` as defined by the standard contract.
- [ ] Subagents do not write directly to the report, except for the explicitly authorized report writer.

## Dependencies

- [ ] Required skills are declared in `references/DEPENDENCIES.md` or `SKILL.md` frontmatter.
- [ ] Adapter skills are declared as dependencies.
- [ ] `token-resolver` and `detect-project-context` are declared.
- [ ] Consumed context reports are declared.
- [ ] Required external tools, APIs, MCP servers, and env vars are documented.
- [ ] Absence of an optional dependency is handled gracefully.

## Security

- [ ] No secrets are hardcoded.
- [ ] Tokens are referenced by env var names or extracted from MCP config by `token-resolver`.
- [ ] Tokens are not logged in report or state files.

## Scenarios to walk through

1. First run with no config — skill asks for missing values and persists them.
2. Second run on the same PR — skill reads state and reports deltas.
3. PR with only bot comments — skill challenges and downgrades appropriately.
4. PR with failing CI — skill surfaces blocker and summarizes logs.
5. Context compaction mid-run — skill resumes from the pending phase.
6. Unsupported PR platform — skill falls back to `manual-pr-adapter` without failing.
7. Missing CI/static-analysis/issue-tracker — skill reports plainly and continues.
8. Better tool available than configured adapter — skill discloses the better tool and asks before accepting degraded data.
9. Degraded source accepted — skill records the degraded source and the better alternative in the Data sources section.
