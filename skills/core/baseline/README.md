# baseline

Capture a reproducible snapshot of the current state of a feature, module, route, API, or bug on a specified branch. The snapshot becomes a trusted reference point for later work.

This is a standalone, global conductor. It does not depend on other skills, but it can consume context reports from other skills or the user when their filename or frontmatter matches the current scope, ticket, or branch.

## Usage

```
baseline
baseline SHB-283
baseline auth-guard-race-condition
reproduce this bug
capture pre-change UI
verify UI
```

## Skill metadata

| Attribute | Value |
|---|---|
| Type | Conductor |
| Invocation | Model-invoked |
| Scope | Global |
| Leading word | Capture |
| Version | 1.0.0 |

## Output paths

- Markdown report: `.agents/context/baseline/{scope}-{branch}.md`
- Optional HTML gallery: `.agents/context/baseline/{scope}-{branch}.html`
- Artifacts: `.agents/context/baseline/{scope}-{branch}/`

`{scope}` and `{branch}` are slugified.

## Scripts

Read-only helper scripts. They do not mutate project files.

| Script | Purpose |
|---|---|
| `detect-project-type.py` | Classify the project. |
| `detect-baseline-method.py` | Detect viable capture methods. |
| `resolve-git-scope.py` | Resolve branch, commit, and scope. |
| `scan-related-context.py` | Find related context reports, excluding baseline outputs. |
| `check-target-reachable.py` | Check URL or file path reachability. |

## State and resumption

State file: `.agents/context/baseline/.state/{scope}-{branch}.json`.

- Resume from the last step if branch and commit still match.
- Archive stale state with `.stale` and start fresh if they differ.
- Record pending `needs_input` questions and resume after the user answers.
- On success, archive the state to `-completed.json` or remove it.

## Evaluation plan

Trigger evals live in `evals/evals.json` and cover realistic invoke phrases such as `baseline`, `reproduce`, `check the app`, `verify UI`, `capture state`, and `snapshot`.

Behavior evals cover: missing required capabilities, ambiguous scope, missing tooling for selected method, stale state, user rejects branch switch, and manual fallback.

Report evals cover: required frontmatter present; `reproducible` only for `type: bug`; consumed context excludes baseline outputs.

Review cadence: validate on every minor/major version bump and at least quarterly.

## Maintenance

- Keep `SKILL.md` focused on intent and delegation; detail lives in `references/`.
- Preserve existing user preferences when updating config.
- Keep report `version` in sync with the skill's version.
