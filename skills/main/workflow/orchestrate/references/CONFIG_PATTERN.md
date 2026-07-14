# Configuration Pattern

Orchestrate uses a project-level config file plus per-run state.

## Config file

Path: `.agents/config/orchestrate.yaml`

```yaml
default_base_branch: origin/development
branch_naming_pattern: "{key}"
protected_branches: [main, development, master]

required_context_skills: [debrief, baseline]
preferred_challenge_skills: [grill-with-docs, grill-me, zoom-out]
implementation_skills: [tdd, implement]
verification_skills: [verify-branch]
checkpoint_skill: handoff

auto_mode_default: false
require_user_confirm_before_plan: true
require_user_confirm_before_execution: true

coding_standards_path: docs/agents/coding-standards.md

output_dir: .agents/context/orchestrate

notes: []
```

## Field reference

| Field | Purpose |
|-------|---------|
| `default_base_branch` | Base branch to pull before creating a feature branch. |
| `branch_naming_pattern` | Pattern for the feature branch name. `{key}` is replaced with the ticket key. |
| `protected_branches` | Branches that must not be checked out as a feature branch. |
| `required_context_skills` | Skills that must produce a report before orchestration can plan. |
| `preferred_challenge_skills` | Skills that may be used for the challenge gate. |
| `implementation_skills` | Preferred implementation skills, in order. |
| `verification_skills` | Skills that verify a phase or branch. |
| `checkpoint_skill` | Skill used for handoff checkpoints. |
| `auto_mode_default` | Default auto mode when not specified by the user. |
| `require_user_confirm_before_plan` | Whether to stop for confirmation before drafting a plan. |
| `require_user_confirm_before_execution` | Whether to stop for confirmation before executing a plan. |
| `coding_standards_path` | Path to project coding standards. |
| `output_dir` | Root directory for orchestration outputs. |
| `notes` | Persistent observations about the user's orchestration preferences. |

## Detect / ask / persist / reuse

1. **Detect** — check if `.agents/config/orchestrate.yaml` exists and has all required fields.
2. **Ask** — if any required field is missing, ask the user for a value and the reasoning.
3. **Persist** — write the resolved config back to the file, including the reasoning in `notes`.
4. **Reuse** — on future runs, read the config first and use the resolved settings.

## Notes

The orchestrator appends observations to `notes` as it learns the user's style. Examples:

- User prefers detailed phase contracts.
- User frequently skips `grill-me` for UI-only changes.
- User wants auto-fix limited to formatting issues.

Do not let notes override explicit config values.
