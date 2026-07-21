# Ticket Adapters

`merge-latest` can enrich branch and conflict context with ticket information. Jira enrichment is consumed from the shared building blocks; other trackers use the private adapters below.

## Jira via the shared blocks

When `ticket_tracker_adapter: jira`, the skill delegates to the `jira-adapter` skill, which resolves the ticket and returns the normalized issue-tracker shape (summary, status, acceptance criteria, links). Credentials are resolved through the `token-resolver` skill — never read from config files and never asked for inside this skill.

```yaml
ticket_tracker_adapter: jira
ticket_key_pattern: "[A-Z]+-\\d+"
jira:
  base_url: https://your-domain.atlassian.net
  project_key: SHB
```

Used for resolving ticket keys from branch names, fetching ticket summary/status/linked PRs, and enriching commit context with ticket intent.

If `jira-adapter` or `token-resolver` is not installed, the skill degrades to git metadata and discloses it (see [CAPABILITIES.md](CAPABILITIES.md#degraded-enrichment-disclosure)).

## Private adapters (trackers the blocks do not cover)

### GitHub Issues

```yaml
ticket_tracker_adapter: github
github:
  owner: my-org
  repo: my-repo
```

Used for mapping branch names or commit messages to issue numbers and reading labels, milestones, and linked PRs. Environment: `GITHUB_TOKEN` (resolve via `token-resolver` when available).

### Linear

```yaml
ticket_tracker_adapter: linear
linear:
  team_key: ENG
```

Used for resolving `ENG-123` style keys and fetching issue state and assignee. Environment: `LINEAR_API_KEY`.

### Asana

```yaml
ticket_tracker_adapter: asana
asana:
  project_gid: "1200000000000000"
```

Used for resolving task URLs or custom identifiers and fetching task status, assignee, and due date. Environment: `ASANA_ACCESS_TOKEN`.

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
- Missing or broken adapters are not hard stops; the skill falls back to git metadata and discloses the degradation (see [CAPABILITIES.md](CAPABILITIES.md#degraded-enrichment-disclosure)).
- Keep credential references out of skill files and config; resolve them through `token-resolver` or environment variables.
