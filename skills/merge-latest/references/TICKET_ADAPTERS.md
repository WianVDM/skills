# Ticket Adapters

`merge-latest` can enrich branch and conflict context with ticket information. Adapters are modular and project-specific via config.

## Configuring an adapter

Set the adapter in `.agents/config/merge-latest.yaml`:

```yaml
ticket_tracker_adapter: jira   # jira | github | linear | asana | custom
ticket_key_pattern: "[A-Z]+-\\d+"
```

Each adapter reads credentials from environment variables or the harness secret store; never from the config file.

## Built-in adapter examples

### Jira

```yaml
ticket_tracker_adapter: jira
jira:
  base_url: https://your-domain.atlassian.net
  project_key: SHB
```

Used for:

- Resolving ticket keys from branch names.
- Fetching ticket summary, status, and linked PRs.
- Enriching commit context with ticket intent.

Required environment:

- `JIRA_API_TOKEN` or `JIRA_TOKEN`
- `JIRA_USER_EMAIL` (if using basic auth)

### GitHub Issues

```yaml
ticket_tracker_adapter: github
github:
  owner: my-org
  repo: my-repo
```

Used for:

- Mapping branch names or commit messages to issue numbers.
- Reading issue labels, milestones, and linked PRs.

Required environment:

- `GITHUB_TOKEN`

### Linear

```yaml
ticket_tracker_adapter: linear
linear:
  team_key: ENG
```

Used for:

- Resolving `ENG-123` style keys.
- Fetching issue state and assignee.

Required environment:

- `LINEAR_API_KEY`

### Asana

```yaml
ticket_tracker_adapter: asana
asana:
  project_gid: "1200000000000000"
```

Used for:

- Resolving task URLs or custom identifiers.
- Fetching task status, assignee, and due date.

Required environment:

- `ASANA_ACCESS_TOKEN`

## Custom adapter

A custom adapter is a small script that accepts a ticket key and prints JSON to stdout:

```yaml
ticket_tracker_adapter: custom
custom_adapter:
  command: "node ./scripts/my-ticket-adapter.js"
```

The script receives the ticket key as the first argument and must output:

```json
{
  "key": "SHB-317",
  "summary": "Fix checkout flow",
  "status": "In Progress",
  "url": "https://...",
  "linked_prs": ["https://github.com/org/repo/pull/42"],
  "error": null
}
```

If `error` is non-null, the skill logs the failure and continues without ticket enrichment.

## Adapter contract

- Adapters are read-only. They must not modify code, tickets, or state.
- Adapters return structured JSON.
- Missing or broken adapters are not hard stops; the skill falls back to git metadata.
- Keep credential references out of skill files and config; use environment variables.
