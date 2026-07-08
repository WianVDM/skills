# Dependencies

## Required building blocks

- `worker-contract` — canonical return format for adapter output.
- `token-resolver` — resolves the Jira token from config, env vars, or user input.

## Runtime requirements

- Network access to the configured Jira `base_url` REST API.
- Python 3.x (or equivalent HTTP client) for making Jira API requests.
- One of `JIRA_TOKEN` or `JIRA_API_TOKEN` environment variable (or equivalent resolved token) with permission to read issues in the target project.

## Optional

- `custom_fields` mapping if the Jira instance stores acceptance criteria in a custom field rather than the description.
