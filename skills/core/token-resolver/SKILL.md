---
name: token-resolver
description: Resolve secure tokens for adapters from environment variables, MCP config files, or a one-time user prompt. Return a reference without exposing the secret value.
license: Proprietary
invocation: model-invoked
metadata:
  tags: [security, tokens, adapters, building-block]
  author: Wian van der Merwe
  version: "1.0.1"
---

# Token Resolver

A narrow, reusable building block that resolves tokens and other secrets for adapter skills without exposing them in output files.

## Purpose

Adapters need credentials, but they should not implement their own token discovery logic. `token-resolver` centralizes the resolution order and returns a token reference to the caller.

## Type

Tool building block.

## In scope

- Resolve a token from, in order:
  1. An explicit literal in config.
  2. An environment variable reference (`${TOKEN_NAME}` or `$TOKEN_NAME`).
  3. A configured MCP server config file read as a local file.
  4. A one-time user prompt, persisted as an env-var name or a secure-store reference (e.g., OS keychain or secret manager).
- Validate that the token is present and non-empty.
- Return the resolved token to the caller without logging it.
- Record the source of the token (env var name, MCP config path) in notes, but never the token itself.

## Out of scope

- Validating token permissions against a provider endpoint. Adapters perform that validation.
- Storing tokens in config files. Only env-var names or secure-store references are persisted.
- Asking the user for tokens unless explicitly requested by the caller.

## When to use

- An adapter skill needs a token before calling an external API.
- A conductor needs to resolve multiple provider tokens consistently.
- A skill wants to avoid duplicating env-var and MCP-config parsing logic.

## Inputs

```yaml
---
token_config:
  value: ${GITHUB_TOKEN}      # optional literal or env-var reference
  env_var: GITHUB_TOKEN       # optional preferred env-var name
  mcp_config_sources: []       # optional list of local MCP config file paths to inspect
  mcp_server_key: github      # optional MCP server key
  mcp_token_keys:             # optional token key names in MCP server env
    - GITHUB_TOKEN
    - GITHUB_PERSONAL_ACCESS_TOKEN
---
```

## Outputs

Use the standard worker return contract from `worker-contract`:

```yaml
---
status: complete | needs_input | blocked
---

## Summary
Token resolved from env var `GITHUB_TOKEN`.

## Findings
- Token resolved from: env var `GITHUB_TOKEN`
- Token value: <redacted>

## Decisions made
- Selected env-var source because it was explicitly configured.
- Persisted `GITHUB_TOKEN` as the canonical reference.

## Open questions
- None.

## Blockers
- None.
```

## Completion criteria

| Status | When to return |
|---|---|
| `complete` | A non-empty token was found and returned to the caller without being logged. |
| `needs_input` | The token is missing and the caller has authorized prompting the user once. |
| `blocked` | The token is missing, prompting is not authorized, or the configured source is unreachable. |

## Rules

- Never include the literal token value in `Summary`, `Findings`, `Decisions made`, `Open questions`, `Blockers`, or any artifact.
- If the token is missing, return `status: needs_input` with the exact question and options.
- If the token is provided by the user, store only the env-var name or secure-store reference, not the value.
- If multiple sources are available, prefer the most explicit one configured by the user.
- When reading an MCP config file, treat it as a local file read with the `read` tool; do not invoke an MCP server.

## Dependencies

- `read`, `write`, `edit` tools to inspect config files.
- Python 3.x for deterministic parsing if a script is used.
- Environment variables and local MCP config files referenced by the caller.

## References

- `docs/skill-standards/patterns/configurable.md`
- `docs/skill-standards/patterns/global-pluggable.md`
- `worker-contract` skill
