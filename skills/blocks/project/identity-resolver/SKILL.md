---
name: identity-resolver
description: Resolve a work item from user input. Given a number, URL, branch, ticket key, or arbitrary text, returns a normalized identity with type, key, repo, branch, base, commit, url, and project.
invocation: model-invoked
depends:
  - worker-contract
  - context-reports
  - detect-project-context
  - tool-discovery
---

# identity-resolver

## Purpose

Normalize a vague user input into a concrete work-item identity so downstream skills can operate on a stable `{type, key, repo, branch, ...}` envelope.

## Skill type

Building block. It only resolves identity; it does not fetch data or invoke tools.

## When to use

A conductor needs to know what the user is referring to before it can load context, fetch reports, or call adapters. Use `identity-resolver` when the input might be a PR number, URL, branch, ticket key, or commit hash.

## In scope

- Resolve user input to one of the supported work-item types.
- Extract ticket keys from branch names or text.
- Parse PR numbers and PR URLs.
- Detect the current branch and repo from git state.
- Return a normalized identity envelope.

## Out of scope

- Fetching PR metadata, ticket scope, or any other data.
- Resolving tokens or calling adapters.
- Deciding which tool to use (use `tool-discovery`).

## Core contract

Accepts `user_input` plus optional context (`repo`, `branch`, `work_item_type`). Returns a normalized identity envelope. If the input is ambiguous, returns `needs_input` with a reason.

## Supported work-item types

| Type | How it is recognized |
|---|---|
| `ticket` | Text matches `[A-Z][A-Z0-9]*-\d+`. |
| `pr` | Digits, a PR URL (`owner/repo/pull/number`), or a branch/ticket that resolves to a PR. |
| `branch` | Explicit branch name or current git branch. |
| `commit` | A 40-character hex string or valid git commit hash. |

## Operations

- `resolve` — return a normalized identity.

## Input

```json
{
  "operation": "resolve",
  "user_input": "42",
  "context_dir": ".agents/context",
  "config_dir": ".agents/config",
  "repo": "owner/repo",
  "branch": "feature/OC-1234"
}
```

## Output

```json
{
  "status": "found",
  "type": "pr",
  "key": "42@owner-repo",
  "repo": "owner/repo",
  "branch": "feature/OC-1234",
  "base": "main",
  "commit": "abc1234",
  "url": "https://github.com/owner/repo/pull/42",
  "project": "OC",
  "source": "user_input"
}
```

See [references/INTERFACE.md](references/INTERFACE.md) for the full schema.

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- [Interface](references/INTERFACE.md)
- [Dependencies](references/DEPENDENCIES.md)
