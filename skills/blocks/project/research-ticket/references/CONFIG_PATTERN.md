# Tracker Config Pattern

`research-ticket` does not own its own configuration. The caller skill passes a `tracker_config` object that contains tracker-specific connection details and credential environment variable names.

## Top-level input fields

| Field | Required | Type | Description |
|---|---|---|---|
| `ticket_key` | yes | string | Ticket or issue key to research. |
| `project` | no | string | Project key, if known. Used for validation only. |
| `tracker` | yes | string | Tracker type: `jira`, `github`, `linear`, or `manual`. |
| `tracker_config` | yes | object | Tracker-specific configuration. |
| `scope` | no | string[] | Data categories to fetch. Defaults to all. |
| `manual_context` | no | object | Required when `tracker: manual`. |

## `tracker_config` schema

All trackers share the following common fields:

| Field | Required | Type | Description |
|---|---|---|---|
| `token_env` | yes | string | Name of the environment variable that holds the API token. |

Tracker-specific fields:

### `jira`

```yaml
tracker: jira
tracker_config:
  server_url: https://your-domain.atlassian.net
  token_env: JIRA_API_TOKEN
  username_env: JIRA_USERNAME
```

| Field | Required | Description |
|---|---|---|
| `server_url` | yes | Base URL of the Jira instance. |
| `token_env` | yes | Env var name for the API token or password. |
| `username_env` | no | Env var name for the username/email when using basic auth. |

### `github`

```yaml
tracker: github
tracker_config:
  token_env: GITHUB_TOKEN
  repo: owner/repo
```

| Field | Required | Description |
|---|---|---|
| `token_env` | yes | Env var name for the GitHub token. |
| `repo` | yes | Repository in `owner/repo` format. |

### `linear`

```yaml
tracker: linear
tracker_config:
  token_env: LINEAR_API_KEY
  team: ENG
```

| Field | Required | Description |
|---|---|---|
| `token_env` | yes | Env var name for the Linear API key. |
| `team` | no | Team identifier used to resolve issue identifiers. |

### `manual`

```yaml
tracker: manual
tracker_config: {}
manual_context:
  summary: "Auth guard race condition"
  description: "..."
  status: "Open"
  priority: "High"
  assignee: "..."
  reporter: "..."
  labels: ["auth", "bug"]
  components: ["Frontend"]
  acceptance_criteria: ["..."]
  comments: []
  attachments: []
  history: []
  dev_info:
    prs: []
    branches: []
    commits: []
  related_tickets:
    parent: null
    children: []
    duplicates: []
    linked: []
    blocked_by: []
    blocks: []
  worklog: []
```

When `tracker: manual`, the `tracker_config` object may be empty and all ticket data is provided through `manual_context`. The skill maps `manual_context` fields onto the normalized output schema.

## Scope values

The `scope` array controls which categories are returned. If omitted, all categories are returned.

| Value | Description |
|---|---|
| `core` | Core ticket fields (summary, description, status, priority, assignee, reporter, labels, components, dates). |
| `comments` | Chronological comment list. |
| `attachments` | Attachment metadata. |
| `history` | Status transitions. |
| `dev_info` | Linked PRs, branches, and commits. |
| `related` | Parent, children, duplicates, linked, blocked-by, and blocks. |
| `worklog` | Time tracking entries. |

## Notes

- All tracker calls in v1 use REST APIs via `bash` and environment variables. MCP server support is not implemented.
- Jira `dev_info` is returned only when the `development` field is provided by the server; otherwise the response is `partial` with a gap note.
