# Config pattern

Configuration schema and first-run flow for `pr-review`.

## Config file

`{config_dir}/pr-review.yaml`

## Schema

```yaml
pr-review:
  tools:
    pr-source:
      provider: auto  # auto, github, manual
    reviews:
      provider: auto
    changed-files:
      provider: auto
    ci:
      provider: auto
    issue-tracker:
      provider: auto
    checkout:
      provider: auto  # auto, worktree, clone, manual
    posting:
      provider: auto  # auto, github-mcp, gh-cli, manual
  tooling:
    preference: best  # best, local, configured
    degraded_mode: ask  # ask, accept, reject
  review:
    default_event: REQUEST_CHANGES
    require_tests_for_new_logic: true
    allow_post_without_confirmation: false
  gates:
    - name: typecheck
      command: npm run typecheck -- {files}
    - name: lint
      command: npm run lint -- {files}
  project_conventions:
    - "Every new API endpoint must have a test."
    - "Use bcrypt for password hashing."
```

## First-run flow

1. Detect project context with `detect-project-context`.
2. Load existing config if present.
3. If missing, invoke `initialize-skill` with defaults.
4. Propose the merged config to the user.
5. Only write after explicit `--approve`.

## Gate commands

Gate commands use the `{files}` placeholder to receive the list of changed files. If no placeholder is present, files are appended.

## Provider values

- `auto` — let `tool-discovery` choose the best available tool.
- `github` / `github-mcp` / `gh-cli` — prefer the GitHub tool.
- `worktree` — use `git-worktree-inspector` for local checkout.
- `manual` — prompt the user for input or use a manual adapter.
