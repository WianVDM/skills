# Validation

Before considering the skill complete or using it in a real run:

## Frontmatter

- [ ] `name` is lowercase with hyphens and matches the directory name.
- [ ] `description` is under 1024 characters and includes triggers.
- [ ] `license` and `metadata` are present.

## SKILL.md

- [ ] Focuses on intent and guidelines, not exact commands.
- [ ] Declares skill type (workflow).
- [ ] Lists out-of-scope behavior.
- [ ] Links to all reference files.

## References

- [ ] All linked reference files exist.
- [ ] `CONFIG_PATTERN.md` documents detect/ask/persist/reuse.
- [ ] `CONFIG_PATTERN.md` explains harness/provider detection from env vars and configured MCP config paths, with examples rather than hardcoded defaults.
- [ ] `CONTEXT_REPORTS.md` documents output schemas and locations.
- [ ] `CONTEXT_REPORTS.md` documents generic context scanning, relevance from frontmatter, and fallback behavior.
- [ ] `CAPABILITIES.md` documents provider detection.
- [ ] `CAPABILITIES.md` describes harness detection without hardcoded harness names.
- [ ] `PROVIDER_ADAPTERS.md` and `CI_ADAPTERS.md` define adapter interfaces.
- [ ] `COMMENT_TRIAGE.md` documents source weighting and challenge rules.
- [ ] `CHECKPOINTING.md` documents phases and resume rules.
- [ ] `REFERENCE.md` documents skill version vs report/state schema version and migration strategy.

## Subagents

- [ ] Each subagent has a narrow scope.
- [ ] Each subagent uses the standard worker return format.
- [ ] Each worker returns `status`, `artifacts`, `summary`, `findings`, `decisions made`, `open questions`, and `blockers` as defined by the standard contract.
- [ ] Subagents do not write directly to the report; they return findings for the main agent to integrate.

## Dependencies

- [ ] Required skills are declared in `references/DEPENDENCIES.md` or `SKILL.md` frontmatter.
- [ ] Consumed context reports are declared.
- [ ] Required external tools, APIs, MCP servers, and env vars are documented.
- [ ] Absence of an optional dependency is handled gracefully.

## Security

- [ ] No secrets are hardcoded.
- [ ] Tokens are referenced by env var names or extracted from MCP config.
- [ ] Tokens are not logged in report or state files.

## Scenarios to walk through

1. First run with no config — skill asks for missing values and persists them.
2. Second run on the same PR — skill reads state and reports deltas.
3. PR with only bot comments — skill challenges and downgrades appropriately.
4. PR with failing CI — skill surfaces blocker and summarizes logs.
5. Context compaction mid-run — skill resumes from the pending phase.
