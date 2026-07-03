# Config pattern for skill-name

## Config location

This skill reads configuration from `{config}/skill-name.yaml` and shared values from `{config}/shared.yaml`.

`{config}` is the detected config directory for the project. See `references/PLUGGABILITY.md` in the `write-a-skill` conductor for detection rules.

## Config keys

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `example_key` | yes | — | What this key controls. |
| `optional_key` | no | `default_value` | What this key controls. |

## Bootstrap routine

This skill follows a load-detect-validate-resolve-persist-execute-curate routine.

- Load existing shared config and skill-specific config.
- Detect the environment.
- Validate whether config matches the environment and is sufficient.
- Resolve ambiguity by asking the user.
- Persist choices and reasoning.
- Execute using resolved config.
- Curate notes afterward.

## Notes

Notes are memory, not logs. Add a note only when the information changes how a future invocation behaves.

| Category | Purpose |
|----------|---------|
| `workaround` | A non-obvious method that worked. |
| `preference` | User's stated preference. |
| `assumption` | Something taken as true that could change. |
| `gotcha` | A trap the skill hit. |
| `decision` | A deliberate choice with rationale. |
