---
name: research-ticket
description: "Fetch and normalize all data about a ticket from a configured issue tracker, including core fields, comments, attachments, history, development info, and related tickets. Use when a skill needs ticket context before making decisions or recommendations."
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [ticket, issue-tracker, research, building-block]
license: Proprietary
depends:
  - context-reports
  - worker-contract
---

# research-ticket

## Purpose

`research-ticket` is a building-block skill that abstracts ticket fetching across multiple issue trackers (Jira, GitHub, Linear) plus a manual fallback. It returns a normalized, tracker-agnostic representation of a ticket and its related context.

It does not form assumptions, explore the codebase, or decide what to do next.

## Skill type

Building block / data adapter.

## When to use

- A conductor needs to understand a ticket before proceeding.
- A skill needs normalized ticket data as input.
- The user wants to fetch ticket context without running a full debrief or workflow.

## Core contract

Accepts a `ticket_key`, `tracker` type, and `tracker_config`. Fetches the requested `scope` of data from the selected tracker and returns a normalized envelope with `status`, `ticket`, `comments`, `attachments`, `history`, `dev_info`, `related_tickets`, `worklog`, and a `context_graph`.

If the tracker is not `manual` and credentials are missing or the API call fails, the skill returns `status: needs_input` with the missing environment variable names listed. It does not prompt the user directly.

## In scope

- Fetch core ticket fields: key, summary, description, status, priority, assignee, reporter, labels, components, created/updated dates.
- Fetch comments chronologically.
- Fetch attachment metadata and, when possible, summaries or downloaded content.
- Fetch status history / transitions.
- Fetch acceptance criteria (explicit or inferred from the description).
- Fetch development info: linked PRs, branches, commits.
- Fetch raw related ticket references from the tracker: parent, children, duplicates, linked, blocked-by, blocks.
- Fetch worklog / time tracking if available and requested.
- Support manual fallback when no tracker is configured.
- Return a normalized context graph of the sources this skill fetched.

## Out of scope

- Forming assumptions about intent.
- Exploring the codebase.
- Asking the user questions directly. Missing credentials are surfaced as `needs_input`.
- Recommending next steps.
- Writing files unless explicitly instructed to cache output.

## Input / output contract

### Input

```yaml
---
ticket_key: OC-4644
project: OC
tracker: jira
tracker_config:
  server_url: https://your-domain.atlassian.net
  token_env: JIRA_API_TOKEN
  username_env: JIRA_USERNAME
scope:
  - core
  - comments
  - attachments
  - history
  - dev_info
  - related
  - worklog
manual_context:
  summary: "..."
  description: "..."
```

| Field | Required | Description |
|---|---|---|
| `ticket_key` | yes | Ticket or issue key to research. |
| `project` | no | Project key, if known. Used for validation. |
| `tracker` | yes | Tracker type: `jira`, `github`, `linear`, or `manual`. |
| `tracker_config` | yes | Tracker-specific config (env var names, repo, team, server URL). |
| `scope` | no | Data categories to fetch. Defaults to all categories. |
| `manual_context` | no | User-provided context when `tracker: manual`. |

### Output

```yaml
---
status: complete
ticket:
  key: OC-4644
  source: jira
  summary: "Auth guard race condition"
  description: "..."
  issue_type: "Bug"
  status: "In Progress"
  priority: "High"
  assignee: "..."
  reporter: "..."
  created_at: "2026-07-01T10:00:00Z"
  updated_at: "2026-07-03T08:42:00Z"
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
context_graph: []
---
```

| Status | Meaning | Caller action |
|---|---|---|
| `complete` | All requested data fetched and normalized. | Continue. |
| `partial` | Some data unavailable or truncated. | Note gaps and continue with reduced confidence. |
| `needs_input` | Credentials, scope, or tracker choice needed. | Surface question to user. |
| `blocked` | Unrecoverable error (tracker unavailable, key invalid). | Report blocker and offer alternatives. |

## Tracker adapters

`research-ticket` internally dispatches to tracker-specific adapters.

| Adapter | Source | Notes |
|---|---|---|
| `jira` | REST API via env vars | Richest metadata; supports parent/child, links, worklog. |
| `github` | GitHub API via env vars | Issue-centric; PR links via development info. |
| `linear` | Linear API via env vars | Team-based identifiers; supports related issues. |
| `manual` | User-provided context | No API calls; user provides summary, description, acceptance criteria, and related context. |

The script implementing this skill (`scripts/research-ticket.py`) reads JSON from stdin and writes JSON to stdout. It is deterministic and can be invoked by the model directly or by a conductor.

## Lazy loading

Only the selected tracker adapter is initialized. Other trackers and their credentials are not inspected. If credentials are missing, the skill returns `needs_input` rather than prompting the user.

## Dependencies

- **Required skills**: `context-reports`, `worker-contract`.
- **Required tools**: `read`, `bash`.
- **Recommended tools**: None in v1.0.0; the skill uses REST API calls via `bash` and environment variables.
- **Required binaries**: Python 3.x for the deterministic helper script.
- **Environment variables**: Referenced through `tracker_config`, not hardcoded. Common examples include `JIRA_API_TOKEN`, `JIRA_USERNAME`, `GITHUB_TOKEN`, and `LINEAR_API_KEY`.

See [`references/DEPENDENCIES.md`](references/DEPENDENCIES.md) and [`references/CONFIG_PATTERN.md`](references/CONFIG_PATTERN.md) for the full dependency and config schema reference.

## Configuration

Config lives with the caller skill (e.g., `debrief.yaml`), not inside `research-ticket`. The caller passes `tracker_config` to `research-ticket`.

Example caller config:

```yaml
preferences:
  issue_tracker: jira
trackers:
  jira:
    server_url: https://your-domain.atlassian.net
    token_env: JIRA_API_TOKEN
    username_env: JIRA_USERNAME
  github:
    token_env: GITHUB_TOKEN
    repo: owner/repo
  linear:
    token_env: LINEAR_API_KEY
    team: ENG
```

## Security

- No plaintext secrets in skill files.
- Tokens are referenced via env var names in config.
- Read-only by default; does not modify trackers.
- REST API calls are used in v1; MCP server support is not yet implemented.

## Example usage by a conductor

```text
Run research-ticket with ticket_key OC-4644, tracker jira, and tracker_config from {marker_dir}/config/debrief.yaml. Fetch core, comments, attachments, dev_info, and related.
```

## Known limitations

- `acceptance_criteria` is inferred only when an explicit "Acceptance criteria" or "AC" header is present in the description; it stops at the next markdown heading.
- GitHub `history` (status transitions) is not fetched in v1; the field is returned empty.
- Jira `dev_info` is read from the `development` field when the server provides it. If that field is absent, the response is `partial` with a gap note rather than a silently empty object.
- MCP server invocation is not implemented in v1. All tracker calls use REST APIs via `bash` and environment variables.

## Resolved design decisions

1. **Caching**: Callers own caching and freshness. `research-ticket` does not write files unless explicitly asked.
2. **Tracker adapters**: Adapters stay internal to `research-ticket` for the first version. Splitting them into sub-skills is deferred until a second tracker adapter needs to be reused elsewhere.
3. **Large content**: Comments and attachments are truncated to a configured limit; summaries may be generated for binary/image attachments.
4. **Acceptance criteria inference**: A lightweight extraction is performed when explicit criteria are not present.
5. **Multiple trackers in one call**: `research-ticket` uses one tracker per call. Cross-tracker merging is out of scope.

## References

- [`references/DEPENDENCIES.md`](references/DEPENDENCIES.md)
- [`references/CONFIG_PATTERN.md`](references/CONFIG_PATTERN.md)
- `docs/skill-standards/schemas/skill-frontmatter.schema.json`
- `docs/skill-standards/schemas/evals.json.schema.json`
