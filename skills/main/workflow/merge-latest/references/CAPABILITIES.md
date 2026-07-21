# Capability Detection

`merge-latest` detects what tools, remotes, and project types are available.

## VCS detection

The skill requires a git repository. Verify:

- `.git` directory exists.
- `git` command is available.
- The repository has at least one remote.

If git is unavailable, stop and explain.

## Remote detection

1. If `remote` is set in config, use it.
2. Otherwise infer from `git remote -v`:
   - Prefer `origin` if present.
   - If only one remote exists, use it.
   - If multiple remotes exist and none is `origin`, ask the user and persist the choice.
3. Verify the remote has refs for the target and upstream branches. If a remote tracking ref is missing, stop and ask.

## Authentication and private remotes

If the remote is private or requires authentication:

1. Prefer SSH keys or configured credential helpers.
2. If `git fetch` fails with an authentication error, stop and explain the failure.
3. Do not ask the user for credentials directly inside the skill.
4. Direct the user to configure git authentication (SSH key, credential helper, or environment token) and retry.

For GitHub private repositories, the `GITHUB_TOKEN` environment variable may be used by some harnesses or adapters, but the skill itself does not read secrets.

## Working tree state

Distinguish between modified tracked files and untracked files before deciding whether to proceed:

- **Modified tracked files**: can conflict with a checkout or merge. Stop unless stashing is approved.
- **Untracked files**: do not affect git checkout or merge operations. Warn the user and allow continuing.
- **Staged changes**: treated as modified tracked files.

## Binary files

Binary files are detected by `git diff --numstat` showing no line counts, or by file extension/magic number heuristics. Binary file conflicts are always classified as `review` and surfaced to the user. They are never auto-resolved.

## Build system detection

The validation pipeline auto-detection inspects project files to identify candidate commands. See [VALIDATION.md](VALIDATION.md) for the full detection rules.

## Ticket adapter detection

If `ticket_tracker_adapter` is configured, verify the adapter is usable:

| Adapter | Required evidence |
|---|---|
| `jira` | `jira-adapter` skill installed; `token-resolver` resolves Jira credentials (e.g. `JIRA_API_TOKEN`); `jira.base_url`, `jira.project_key` set |
| `github` | `github.owner`, `github.repo`, and `GITHUB_TOKEN` env var |
| `linear` | `linear.team_key` and `LINEAR_API_KEY` env var |
| `asana` | `asana.project_gid` and `ASANA_ACCESS_TOKEN` env var |
| `custom` | `custom_adapter.command` exists and is executable |

If detection fails, fall back to git metadata. A missing adapter is not a hard stop.

## Degraded enrichment disclosure

Whenever enrichment falls back to a weaker source — a missing ticket adapter, an unavailable MCP server, a degraded recon preview — the skill must say so in its user-facing output: name the stronger source that was unavailable, state what the fallback is, and continue only with the user's consent or a persisted config note recording the preference. Silent degradation is not allowed.

## Script runtime

The bundled scripts require Node.js. Verify:

- `node` command is available.
- `npm` is available (for diagnostics if scripts fail).

If Node.js is unavailable, stop and explain.

Scripts used by this skill:

- `scripts/parse-args.js` — parse invocation tokens.
- `scripts/infer-base.js` — score base-branch candidates.
- `scripts/conflict-brief.js` — extract conflict versions and context.
- `scripts/recon.js` — gather merge metadata.
- `scripts/change-summary.js` — extract timelines, overlap, and hotspots for the pre-merge brief.
- `scripts/resolve-trivial.js` — safe trivial conflict resolution.
- `scripts/report.js` — generate report and chat summary.

## MCP enrichment

For deep conflict analysis, the skill may use:

- GitHub MCP or REST — PR metadata, commit context, author info.
- Jira MCP — ticket context for branch names containing ticket keys.

If these are unavailable, fall back to git metadata and configured ticket adapters — with the disclosure rule above.
