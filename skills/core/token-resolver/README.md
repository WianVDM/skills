# token-resolver

Resolve secure tokens for adapter skills without exposing them in files or output.

## Purpose

Centralizes the logic for resolving tokens from environment variables, MCP server config, or a one-time user prompt. Adapters call this building block instead of implementing their own token discovery.

## When to use

- An adapter needs a provider token.
- A conductor needs to resolve multiple tokens consistently.

## Inputs

A token config specifying the preferred env-var name, optional MCP config sources, and MCP token key names.

## Outputs

A structured result with the resolved token (redacted in output) and the source reference. The skill never logs the token value.

## Security

- Tokens are never written to config files or reports.
- Only env-var names or secure references are persisted.
