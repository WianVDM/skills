# Configuration and Notes

`plan-next` uses the config + notes pattern to learn user planning preferences over time.

## Canonical location

```text
{project-root}/.agents/config/plan-next.yaml
```

## Schema

```yaml
# Harness detection: auto | kimi | claude | gemini | vscode | manual
harness: auto

# Paths to search for skills. Detected harness may add defaults.
skill_search_paths:
  - ~/.agents/skills

planning_preferences:
  default_detail_level: detailed      # concise | detailed | exhaustive
  default_flexibility: moderate       # rigid | moderate | flexible
  max_phases_default: 4
  always_include_understand_phase: true
  default_verification_skills: [verify-branch, baseline]
  show_revision_diffs: true

user_profile:
  commonly_accepted_skills: []
  commonly_rejected_skills: []
  corrections_history: []
  risk_tolerance: cautious            # cautious | balanced | fast

notes: []
```

## First-run flow

1. Load existing config if present.
2. Detect harness and default skill search paths.
3. Ask for missing planning preferences with sensible defaults.
4. Persist config.

## Self-updates

Append observations to `notes` such as:

- "User consistently accepts `grill-with-docs` for PR review plans."
- "User prefers fewer phases for bug reports."
- "User often rejects `prototype` unless UI is uncertain."

Rules:

- Append-only for notes.
- Do not overwrite user values silently.
- Timestamp observations.
