# Configuration and Notes

`merge-latest` uses the config + notes pattern. It detects project settings on first run, asks for missing information, persists the answers, and learns user preferences over time.

Project-specific conventions belong in `notes` so the AI can use them as **guidance**, not as immutable rules or logs.

## Canonical location

```text
{project-root}/.agents/config/merge-latest.yaml
```

## Schema

```yaml
# Default remote name. If omitted, the skill infers it from git.
remote: origin

# Default base branch when inference fails or no history is available
default_base_branch: origin/development

# Branches the skill refuses to modify. Behavior is always hard-refuse;
# there is no warn/confirm override.
protected_branches:
  - main
  - development
  - master

# Merge strategy. `prefer_rebase` was removed; migrate `prefer_rebase: true`
# to `merge_strategy: rebase-if-clean`.
merge_strategy: merge                # merge | rebase-if-clean | ask

# Validation pipeline
validation:
  mode: auto                         # auto | custom
  commands:
    - name: build
      command: npm run build
  timeout_seconds: 600

# Verification tiers (see VALIDATION.md). The pipeline above is tier 1.
verification:
  mode: ask                          # ask | auto — confirm the tier at the pre-merge gate
  max_tier: interactive              # pipeline | re-review | interactive (ceiling)
  dev_server_url: null               # e.g. http://localhost:3000 — never guessed
  ui_tool: auto                      # auto | repo-suite | playwright-mcp | manual

# Legacy build command (migrated to validation.commands on first run)
# Deprecated — removal planned in a future version.
build_command: auto                  # auto | custom | deprecated
custom_build_command: null

# Stash behavior
auto_stash: false                    # if true, stash dirty tree automatically

# Deep conflict analysis threshold
deep_analysis_threshold:
  files: 5
  conflict_blocks: 10

# Conflict resolution policy
preserve_target_by_default: true

# Ticket integration
ticket_key_pattern: "[A-Z]+-\\d+"
ticket_tracker_adapter: null         # jira | github | linear | asana | custom

# GitHub adapter (when ticket_tracker_adapter is github)
github:
  owner: null
  repo: null

# Jira adapter (when ticket_tracker_adapter is jira)
jira:
  base_url: null
  project_key: null

# Custom adapter (when ticket_tracker_adapter is custom)
custom_adapter:
  command: null

# Output and backup
output_dir: .agents/context/merge-latest
backup_retention_days: 30
max_backups: 10

# AI-written observations
notes: []
```

## Notes are guidance, not logs

The `notes` array holds project-specific guidance for the AI. Examples:

- "Feature branches for `one-click-app` are usually stacked on `OC-3626`."
- "Use `origin/development` as the base branch unless the branch name starts with `hotfix/`."
- "The file `package-lock.json` is generated; never auto-resolve it."
- "Validation commands are `npm run type-check`, `npm run build`, and `npm run test`."

Rules for notes:

- Write them as guidance the AI should consider, not as enforced commands.
- The AI may override a note when the current situation clearly contradicts it.
- Append-only by default; do not overwrite user values silently.
- Timestamp observations when the source matters.

## First-run flow

1. Load existing config if present.
2. Detect remote, validation commands, and ticket adapter from project files.
3. Ask user to confirm or override:
   - Default base branch
   - Remote name
   - Protected branches
   - Validation commands
   - Auto-stash preference
   - Ticket tracker adapter
4. Persist config.

## Self-updates

Append observations to `notes` such as:

- "User prefers to merge `origin/development` into feature branches."
- "Validation commands auto-detected as `npm run build` and `npm run test`."
- "User rejected auto-stash; always require clean tree."
- "Stacked feature branches for OC-3626 usually base on OC-3626."

Rules:

- Append-only for notes.
- Do not overwrite user values silently.
- Timestamp observations when useful.
