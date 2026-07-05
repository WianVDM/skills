---
name: detect-project-context
description: Detect the project root, harness, skill directories, config directories, and conventions for any workspace.
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [project-detection, building-block, global, pluggable]
  verification_level: declared
  provenance:
    authored_by: mixed
    generated_by: agent
    origin: foreground
    reviewed_by: audit-skill
    reviewed_at: "2026-07-05T00:00:00Z"
    parent_session: write-a-skill-refactor
---

# detect-project-context

## Purpose

Detect the project root and recommended directories for skills, context, and config so that global skills can avoid hardcoded paths.

## Type

Building block.

## In scope

- Search upward from a starting directory for a known project marker directory.
- Recommend skills, context, and config directory candidates.
- Report confidence based on which expected directories already exist.
- Output results as structured JSON or human-readable text.

## Out of scope

- Writing or creating directories.
- Asking the user for confirmation.
- Detecting harness-specific features beyond directory layout.

## When to use

Another skill or conductor needs to know where project-level skill, context, and config directories live before reading or writing files.

## Steps

1. **Accept optional starting directory.** Default to the current working directory.
   - **Completion criterion:** a resolved starting path is available.
2. **Search upward for a marker directory.** Markers: `.agents`, `.pi`, `agents`.
   - **Completion criterion:** a project root and marker (or none) are identified.
3. **Build candidate directories.** Prefer `{root}/{marker}/{purpose}/`; fall back to common alternatives.
   - **Completion criterion:** candidate lists exist for skills, context, and config directories.
4. **Select recommended directories.** Prefer existing directories; otherwise use the first candidate.
   - **Completion criterion:** recommended paths are chosen for each purpose.
5. **Return structured report.** Include root, marker, confidence, recommended paths, and all candidates.
   - **Completion criterion:** the report is emitted in the requested format.

## Output format

When invoked as a script with `--json`, the report is:

```json
{
  "project_root": "/path/to/project",
  "marker": ".agents",
  "confidence": "high",
  "recommended_skills_dir": "/path/to/project/.agents/skills",
  "recommended_context_dir": "/path/to/project/.agents/context",
  "recommended_config_dir": "/path/to/project/.agents/config",
  "skills_dir_candidates": [...],
  "context_dir_candidates": [...],
  "config_dir_candidates": [...]
}
```

Confidence levels:
- `high`: both skills and context directories exist under the detected marker.
- `medium`: only one expected directory exists.
- `low`: no expected directories exist.

## Security

- This skill is read-only. It does not create, modify, or delete files.
- It does not execute shell commands beyond the internal Python script.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- None.
