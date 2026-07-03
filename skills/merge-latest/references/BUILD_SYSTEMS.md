# Build Systems

`merge-latest` validates merges by running the project build. The build command is detected or configured.

## Detection order

1. If `build_command` is set to a custom value in config, use it.
2. If `build_command` is `auto`, detect from project files.
3. If detection fails or is ambiguous, ask the user.
4. Persist the resolved command in config.

## Supported project types

| Project file | Default command | Notes |
|--------------|-----------------|-------|
| `package.json` | `npm run build` | Check for `yarn.lock` → `yarn build`; `pnpm-lock.yaml` → `pnpm build` |
| `Makefile` | `make` | Run default target |
| `build.gradle` | `./gradlew build` | Fallback to `gradle build` if wrapper missing |
| `pom.xml` | `mvn compile` | Or `mvn test-compile` if tests are expected |
| `pyproject.toml` | user-configured | Python projects vary; ask if not clear |
| `Cargo.toml` | `cargo build` | Rust projects |
| `go.mod` | `go build ./...` | Go projects |

## Build failure handling

If the build fails:

1. Capture the failing output.
2. Run `git merge --abort`.
3. Report result as `aborted`.
4. Ask the user how to proceed.

## Custom build command

If auto-detection is wrong, the user can set:

```yaml
build_command: custom
custom_build_command: "npm run build:prod && npm test"
```
