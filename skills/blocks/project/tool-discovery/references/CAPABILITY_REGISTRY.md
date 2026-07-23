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
        keywords:
          - github
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
- `identifiers` — for `cli`, binary names; for `api`, required env-var names; for `mcp`, tool names matched against the MCP config as an additional signal alongside `keywords`.
- `keywords` — for `mcp`, keywords to match against configured MCP server names (e.g., `github`, `jira`).

MCP matching uses both signals: a tool is available when any keyword or any identifier appears in a detected MCP config file. The `detail` field in the output reports which signal matched (e.g., `MCP keywords github matched` or `MCP identifiers github_get_pull_request matched`).

## Platform coverage

PR, CI, and posting capabilities cover GitHub, GitLab, Azure DevOps, and Bitbucket. Issue-tracker covers Jira, Linear, GitHub Issues, GitLab Issues, and Azure Boards. MCP identifiers use the common tool-naming conventions per provider (`github_*`, `gitlab_*`/`mcp_gitlab_*`, `mcp_ado_*`, `bitbucket_*`); keywords match on server names, so a self-hosted GitLab server named `gitlab` still matches.

## Bundled capabilities

| Capability | Description |
|---|---|
| `pr-source` | Pull-request metadata, changed files, reviews, and threads. |
| `reviews` | Pull-request reviews and inline review threads. |
| `changed-files` | Files changed in a pull request. |
| `ci-source` | CI / build status and job logs. |
| `static-analysis-source` | Static-analysis findings. |
| `issue-tracker-source` | Ticket scope and acceptance criteria. |
| `notification-source` | Feedback from chat, email, or meeting tools. |
| `posting` | Posting reviews or comments back to a platform. |
| `checkout` | Local branch checkout for inspection without disturbing the current branch. |

## Extending the registry

Add new tools to the bundled YAML or pass a custom `registry` path to `discover`. Custom registries must follow the same schema. The bundled registry lives at `scripts/capability-registry.yaml`.

## Relationship to resolution

The registry is about discovery: which known tools exist per capability. Turning a discovered tool into a working, cached recipe — exact calls, field mappings, validation — is covered by [RESOLUTION_GUIDE.md](RESOLUTION_GUIDE.md). Provider-specific adapter skills are deprecated in favor of that flow.
