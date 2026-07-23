# Config pattern

Configuration schema and first-run flow for `pr-review`.

## Config file

`{config_dir}/pr-review.yaml`

## Schema

```yaml
pr-review:
  tools:
    pr-source:
      provider: auto      # auto, github, gitlab, bitbucket, azure, manual
    ci:
      provider: auto      # auto, github, gitlab, azure, manual
    issue-tracker:
      provider: auto      # auto, jira, linear, github-issues, azure-boards, manual
    checkout:
      provider: auto      # auto, worktree, clone, manual
    posting:
      provider: auto      # auto, github-mcp, gh-cli, glab-cli, manual
  tooling:
    preference: best      # best, local, configured
    degraded_mode: ask    # ask, accept, reject
  review:
    default_event: ""     # fallback only; empty means always follow the rubric
    require_tests_for_new_logic: true
    allow_post_without_confirmation: false   # always false
    size_gate_lines: 400
    style:
      approve_opener: "Looks good to me.."
      render_labels: true
      approve_optimistically: true
      optional_comments:
        first_reviewer: allow            # allow, suppress
        after_existing_approval: suppress
      nit_budget: teach-prevent-ux       # teach-prevent-ux, none, allow
      comment_vocabulary: conventional   # conventional, plain
      style_notes: ""
  gates:
    - name: typecheck
      command: npm run typecheck -- {files}
  project_conventions:
    - "Every new API endpoint must have a test."
```

## The style profile

`review.style` is the per-user, per-project preference layer. It controls how reviews read, not what they find — findings come from the rubric, and the style profile can only tighten or loosen how they are presented.

Enforcement points (config keys are inert without these):

- **Synthesizer** — applies `optional_comments` policy using the detected reviewer position, applies `nit_budget`, applies `approve_optimistically` when recommending the event, respects `size_gate_lines`.
- **Writer** — applies `approve_opener`, `render_labels`, format templates, and appends `style_notes` to its rules.

Per-project layering: user-global defaults live under the user config dir; project config overrides them via `initialize-skill`. Example variance: one project wants `"LGTM"` as the opener and no labels rendered; another wants full labels and `after_existing_approval: suppress` because the second approver merges.

## Intake (first run in a project)

On first run, after config is loaded or created, the conductor asks a short set of structured questions — using the harness's question UI where available, plain conversation otherwise — and persists the answers through `initialize-skill`:

1. **Review depth** — thorough (all classes) vs blockers-only. Default: thorough.
2. **Approve opener** — default `"Looks good to me.."`.
3. **Optional comments after an existing approval** — suppress (clean second approval) vs allow. Default: suppress.
4. **Nitpick policy** — teach-prevent-ux, none, allow. Default: teach-prevent-ux.

Ask only what the project has no answer for. If config already resolves a key (user-global defaults or a prior run), skip the question. Intake happens once per project; re-ask only when the user asks to reconfigure or a value proves wrong in use.

## Gate commands

Gate commands use the `{files}` placeholder to receive the changed-file list. If no placeholder is present, files are appended.

## Provider values

- `auto` — resolve via `tool-discovery` (model-first detection, then the cached project recipe).
- A named provider — prefer that provider's tools.
- `manual` — prompt the user for input.
