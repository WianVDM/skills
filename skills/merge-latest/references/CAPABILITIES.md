# Capability Detection

`merge-latest` detects what tools, remotes, and project types are available.

## VCS detection

The skill requires a git repository. Verify:

- `.git` directory exists.
- `git` command is available.
- The repository has at least one remote.

If git is unavailable, consult the user.

## Remote detection

1. If `remote` is set in config, use it.
2. Otherwise infer from `git remote -v`:
   - Prefer `origin` if present.
   - If only one remote exists, use it.
   - If multiple remotes exist and none is `origin`, ask the user and persist the choice.
3. Verify the remote has refs for the target and upstream branches. If a remote tracking ref is missing, stop and ask.

## Build system detection

Inspect project files to determine the build command:

| Project file | Build command candidate |
|--------------|-------------------------|
| `package.json` with `scripts.build` | `npm run build` / `yarn build` / `pnpm build` |
| `Makefile` | `make` |
| `build.gradle` | `./gradlew build` |
| `pom.xml` | `mvn compile` or `mvn test-compile` |
| `pyproject.toml` | configured build task |
| `Cargo.toml` | `cargo build` |
| `go.mod` | `go build ./...` |

If multiple candidates exist, prefer the one matching the most common pattern or ask the user.

## Ticket adapter detection

If `ticket_tracker_adapter` is configured, verify the adapter is usable:

| Adapter | Required evidence |
|---|---|
| `jira` | `jira.base_url`, `jira.project_key`, and `JIRA_API_TOKEN` env var |
| `github` | `github.owner`, `github.repo`, and `GITHUB_TOKEN` env var |
| `linear` | `linear.team_key` and `LINEAR_API_KEY` env var |
| `asana` | `asana.project_gid` and `ASANA_ACCESS_TOKEN` env var |
| `custom` | `custom_adapter.command` exists and is executable |

If detection fails, fall back to git metadata. A missing adapter is not a hard stop.

## Script runtime

The bundled scripts require Node.js. Verify:

- `node` command is available.
- `npm` is available (for diagnostics if scripts fail).

If Node.js is unavailable, consult the user: install Node, provide alternative scripts, or skip script-based helpers.

Scripts used by this skill:

- `scripts/parse-args.js` — parse invocation tokens.
- `scripts/infer-base.js` — score base-branch candidates.
- `scripts/conflict-brief.js` — extract conflict versions and context.
- `scripts/recon.js` — gather merge metadata.
- `scripts/resolve-trivial.js` — safe trivial conflict resolution.
- `scripts/report.js` — generate report and chat summary.

## MCP enrichment

For deep conflict analysis, the skill may use:

- GitHub MCP or REST — PR metadata, commit context, author info.
- Jira MCP — ticket context for branch names containing ticket keys.

If these are unavailable, fall back to git metadata and configured ticket adapters.
