# Capability Detection

`plan-next` discovers what skills are available and what context reports already exist.

## Skill discovery

For each path in `skill_search_paths`:

1. List directories.
2. Check for `SKILL.md` in each.
3. Read frontmatter: `name`, `description`, `metadata`.
4. Build catalog entry.

Also detect built-in skill paths from the harness if available.

## Skill availability sanity check

For each discovered skill, verify:

- `SKILL.md` is readable.
- Core references exist (if the skill declares them).
- Subagent directory exists if the skill claims to use subagents.

If a skill appears incomplete, note it but do not exclude it from evaluation unless it is clearly broken.

## Context report discovery

Check for existing reports in `.agents/context/`:

- `debrief/{key}-report.md`
- `pr-report/{key}-report.md`
- `baseline/{key}-report.md`
- `diagnose/{key}-report.md`

If found, record freshness (last modified time).

## Harness detection

Detect which harness/model is running the skill to find default skill paths and built-in skills. Write detected harness to config `notes`.
