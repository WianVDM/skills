# Validation

Check the skill before considering it complete.

## Mental walkthroughs

Walk through at least two realistic scenarios:

1. A fresh bug with `debrief` and `baseline` already produced.
2. A resume from checkpoint during phase execution.

## Checklist

- [ ] `name` is lowercase with hyphens and matches the directory name.
- [ ] `description` is under 1024 characters and includes triggers.
- [ ] `SKILL.md` focuses on intent and guidelines, not exact commands.
- [ ] Complex detail is in `references/`.
- [ ] Skill type is documented as conductor.
- [ ] State schema and location are documented.
- [ ] Config pattern is documented.
- [ ] Produced reports have documented schemas and locations.
- [ ] Subagent return contract is documented.
- [ ] No harness-specific tool names in `SKILL.md`.
- [ ] Safety rules (no commit/push, user confirmation) are preserved.
- [ ] Examples are included.

## Frontmatter validation

Use `skills-ref validate ./orchestrate` if available.
