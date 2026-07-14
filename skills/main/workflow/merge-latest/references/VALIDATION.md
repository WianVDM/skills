# Merge Validation Pipeline

`merge-latest` validates a merge by running a user-configured pipeline of commands. The pipeline is detected from project files on first run and confirmed with the user before being persisted.

## Why a pipeline

A single "build" command is often not enough to guarantee a safe merge. A TypeScript project, for example, may need to run type checking, linting, the build, and tests. A Java project may need compilation and tests. The skill detects candidate commands and lets the user choose which ones are required.

## Config schema

```yaml
validation:
  mode: auto               # auto | custom
  commands:
    - name: type-check
      command: npm run type-check
    - name: build
      command: npm run build
    - name: test
      command: npm run test
```

- `mode: auto` — detect candidate commands from project files on first run and confirm with the user.
- `mode: custom` — use the user-provided list exactly; no auto-detection.
- `commands` — ordered list of commands to run. Each must succeed for the merge to complete.

## First-run detection

When `validation.commands` is not yet configured, the skill inspects the project and proposes candidate commands:

| Project file | Candidate commands |
|---|---|
| `package.json` with matching scripts | `npm run build`, `npm run test`, `npm run lint`, `npm run type-check` |
| `yarn.lock` present | `yarn build`, `yarn test`, `yarn lint`, `yarn type-check` |
| `pnpm-lock.yaml` present | `pnpm build`, `pnpm test`, `pnpm lint`, `pnpm type-check` |
| `Makefile` | `make`, `make test`, `make lint` |
| `build.gradle` | `./gradlew build`, `./gradlew test` |
| `pom.xml` | `mvn test`, `mvn compile` |
| `pyproject.toml` | detected test/build task |
| `Cargo.toml` | `cargo build`, `cargo test` |
| `go.mod` | `go build ./...`, `go test ./...` |

Only commands that actually exist in the project files are proposed. For example, if `package.json` has no `test` script, `npm run test` is not suggested.

## First-run confirmation flow

1. Present the detected candidate commands with short descriptions.
2. Let the user enable, disable, reorder, or edit each command.
3. Persist the final list under `validation.commands`.
4. Set `validation.mode: auto`.

On later runs, the skill uses the persisted list. If project files change and new candidate commands appear, the skill surfaces them and asks whether to update the saved list.

## Custom mode

If the user sets `validation.mode: custom`, the skill stops auto-detecting and uses the `validation.commands` list exactly. The skill does not modify the list unless the user explicitly edits it.

## Execution rules

1. Run each command in `validation.commands` in order.
2. Capture the output of each command.
3. If any command exits non-zero, abort the merge.
4. If all commands succeed, record the results in the merge report.

## Failure handling

If a validation command fails:

1. Capture the failing output.
2. Run `git merge --abort` (or `git rebase --abort` if rebasing).
3. Report the result as `aborted`.
4. Ask the user how to proceed.

## Timeout

A long-running validation command can hang the merge. The skill should use a configurable timeout (default: 10 minutes) and abort if a command exceeds it. The timeout is stored as `validation.timeout_seconds` in config.

## Default behavior for existing users

For users who have an existing `build_command` or `custom_build_command` in config, migrate it to a single-item `validation.commands` list on first run and ask the user to confirm or add more commands.
