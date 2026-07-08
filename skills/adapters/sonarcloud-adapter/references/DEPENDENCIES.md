# Dependencies

## Required building blocks

- `worker-contract` — canonical return format for adapter output.
- `token-resolver` — resolves the SonarCloud token from config, env vars, or user input.

## Runtime requirements

- Network access to `sonarcloud.io/api`.
- Python 3.x (or equivalent HTTP client) for making SonarCloud API requests.
- One of `SONAR_TOKEN`, `SONARQUBE_TOKEN`, or `SONARCLOUD_TOKEN` environment variable (or equivalent resolved token) with permission to read project issues.

## Optional

- SonarCloud branch/pull-request analysis enabled if scoping by branch or PR.
