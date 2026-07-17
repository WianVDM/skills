# Dependencies

## Required skills

None. The output envelope is tracker-agnostic JSON; conductors wrap it in their own contracts.

## Required tools and capabilities

- `read` — to inspect this skill's `SKILL.md` and reference files when the skill is loaded or invoked.
- `bash` — to run the `scripts/research-ticket.py` helper and to make REST API calls via environment variables.

## Recommended tools and capabilities

None in v1.0.0. All tracker calls use REST APIs via `bash` and environment variables.

## Required binaries

- `python3` — the `scripts/research-ticket.py` script is written in Python 3 and requires no third-party packages.

## Required Python packages

None. The script uses only the Python 3 standard library.

## Environment variables

Environment variables are not hardcoded in the skill. They are referenced by name through `tracker_config`. Common examples include:

- `JIRA_API_TOKEN` — bearer token or API token for Jira.
- `JIRA_USERNAME` — username or email for Jira basic authentication.
- `GITHUB_TOKEN` — personal access token or GitHub App token for the GitHub API.
- `LINEAR_API_KEY` — API key for the Linear GraphQL API.

The actual variable names are configured by the caller in `tracker_config.token_env` (and `tracker_config.username_env` where applicable).

## Required MCP servers

None. MCP server invocation is not implemented in v1.0.0.

## Optional configuration files

- Caller skill config (e.g., `{marker_dir}/config/debrief.yaml`) — contains the `tracker_config` block passed to `research-ticket`.
