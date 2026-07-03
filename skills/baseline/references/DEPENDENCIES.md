# Dependencies

## Required skills

None. `baseline` is a standalone skill.

## Optional consumed context

The skill may scan and read reports from `.agents/context/{type}/{key}.md` when the `key` matches the scope, ticket, or branch. These reports are produced by other skills or by the user; `baseline` does not depend on any specific skill being present.

The skill matches context reports generically by comparing the provided `scope`, `ticket`, or `branch` against the report's filename and frontmatter fields (for example, `scope`, `ticket`, `key`, or `branch`).

These reports are optional. The skill must handle their absence gracefully and must not fail if they are missing. Any reports produced by the `baseline` skill itself are excluded to avoid circular self-reference.

## Required capabilities

- Inspect the current git state (branch, commit, working tree status).
- Detect at least one capture method or obtain user agreement for a manual fallback.

## Required tools

None, but the skill may use any available tool listed in [CAPABILITIES.md](CAPABILITIES.md).

## Environment variables

The skill may reference environment variables through config keys (e.g., `username_env`, `password_env` for authentication). It does not require specific variables by default.
