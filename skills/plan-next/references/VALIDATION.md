# Validation

Before considering the skill complete:

## Frontmatter

- [ ] `name` matches directory name.
- [ ] `description` is under 1024 characters and includes triggers.
- [ ] `license` and `metadata` are present.

## SKILL.md

- [ ] Declares skill type (conductor).
- [ ] Focuses on intent and workflow, not exact commands.
- [ ] Lists out-of-scope behavior.
- [ ] Links to all reference files.

## References

- [ ] All linked reference files exist.
- [ ] `CONFIG_PATTERN.md` documents user profile + preferences.
- [ ] `CAPABILITIES.md` documents skill discovery.
- [ ] `CONTEXT_REPORTS.md` documents outputs and consumed reports.
- [ ] `SUBAGENTS.md` documents delegation contract.
- [ ] `SKILL_PROFILES.md` documents profiling strategy.
- [ ] `CHECKPOINTING.md` documents state and draft/finalize flow.

## Subagents

- [ ] Each subagent has a narrow scope.
- [ ] Each uses the standard worker return format.
- [ ] Workers do not write directly to plan files.

## Scenarios to walk through

1. Bare invocation with no prior context — skill discovers skills and proposes a plan.
2. Invocation after a debrief report — skill consumes it and boosts understanding skills.
3. User asks for "more detailed" — skill shows diff and updates draft.
4. User rejects a recommended skill — skill records preference and adjusts.
5. Context compaction mid-planning — skill resumes from pending phase.
