# Capability Registry

The bundled registry defines known tools for common capabilities. The registry is a YAML file loaded by `scripts/discover-tools.py`.

## Registry format

```yaml
capabilities:
  pr-source:
    description: Pull-request metadata, changed files, reviews, and inline threads.
    tools:
      - name: github-mcp
        category: mcp
        confidence: high
        identifiers:
          - github_get_pull_request
          - github_get_pull_request_reviews
          - github_get_pull_request_files
      - name: gh-cli
        category: cli
        confidence: medium
        identifiers:
          - gh
      - name: github-api
        category: api
        confidence: medium
        identifiers:
          - GITHUB_TOKEN
      - name: manual
        category: manual
        confidence: low
        identifiers: []
```

- `capability` — string identifier.
- `tools` — list of known tools for the capability.
- `name` — tool name returned in discovery output.
- `category` — one of `mcp`, `cli`, `api`, `harness`, `manual`.
- `confidence` — default confidence when the tool is available.
- `identifiers` — for `cli`, binary names; for `api`, required env-var names.
- `keywords` — for `mcp`, keywords to match against configured MCP server names (e.g., `github`, `jira`).

## Bundled capabilities

| Capability | Description |
|---|---|
| `pr-source` | Pull-request metadata, changed files, reviews, and threads. |
| `ci-source` | CI / build status and job logs. |
| `static-analysis-source` | Static-analysis findings. |
| `issue-tracker-source` | Ticket scope and acceptance criteria. |
| `notification-source` | Feedback from chat, email, or meeting tools. |
| `posting` | Posting reviews or comments back to a platform. |

## Extending the registry

Add new tools to the bundled YAML or pass a custom `registry` path to `discover`. Custom registries must follow the same schema. The bundled registry lives at `scripts/capability-registry.yaml`.

## Relationship to adapters

Tool names in the registry should align with adapter skills where possible. For example, `github-mcp` maps to the `github-pr-adapter` contract. The registry is about discovery; adapter contracts define the normalized interface after the tool is selected.
