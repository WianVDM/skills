# baseline

Capture a reproducible snapshot of the current state of a feature, module, route, API, or bug so later sessions have a trusted reference point.

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
| Invocation | User-invoked |
| Scope | Global |
| Leading word | Capture |
| Version | 3.1 |

## Output paths

- Markdown report: `.agents/context/baseline/{scope}-{branch}.md`
- Optional HTML gallery: `.agents/context/baseline/{scope}-{branch}.html`
- Artifacts: `.agents/context/baseline/{scope}-{branch}/`

`{scope}` and `{branch}` are slugified.

## State and resumption

The skill writes a state file at `.agents/context/baseline/.state/{scope}-{branch}.json` after each step. If the skill is interrupted, a later invocation can resume from the last completed step as long as the branch and commit still match. If they differ, the stale state is archived and the workflow starts fresh.

## Evaluation plan

- **Trigger evals:** test that `baseline`, `reproduce`, `check the app`, `verify UI`, and `capture state` invoke the skill, and that unrelated phrases do not.
- **Behavior evals:** missing config, ambiguous scope, no capture method available, stale state file, user rejects branch switch, manual fallback.
- **Review cadence:** validate on every minor/major version bump and at least quarterly.

## Maintenance

- Keep `SKILL.md` focused on intent and workflow; move detailed guidance to `references/`.
- Preserve existing user preferences when updating config or defaults.
- Keep report `version` in sync with the skill's major version.
