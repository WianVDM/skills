# setup-wian-skills

Sync skills from a source package into the current workspace and resolve shared configuration once.

## Usage

```text
/setup-wian-skills
/setup-wian-skills <owner>/<repo>
```

## What it does

1. Resolves target scope (project or user) and source package.
2. Discovers installed skills.
3. Builds and confirms an install/update plan.
4. Applies the approved sync.
5. Collects shared configuration keys once.
6. Presents an initialization checklist for skill-specific setup.
7. Writes a context report.

## References

See `SKILL.md` and the `references/` directory for the full skill contract.
