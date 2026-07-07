# Dependencies

## Declared dependencies

Canonical dependency declarations live in `skills.json` at the skill root. The sections below summarize them for human readers.

## Required skills

None. `baseline` is a standalone skill.

It may reference optional shared conventions from `detect-project-context` and `worker-contract` when available, but it does not require them.

## Recommended skills

None required. The skill works without other skills.

## Optional consumed context

The skill may scan and read reports from `.agents/context/{type}/{key}.md` when the `{key}` matches the scope, ticket, or branch. These reports are produced by other skills or by the user; `baseline` does not depend on any specific skill being present.

The skill matches context reports generically by comparing the provided `scope`, `ticket`, or `branch` against the report's filename and frontmatter fields (for example, `scope`, `ticket`, `key`, or `branch`).

These reports are optional. The skill must handle their absence gracefully and must not fail if they are missing. Any reports produced by the `baseline` skill itself are excluded to avoid circular self-reference.

## Required capabilities

- Inspect the current git state (branch, commit, working tree status).
- Detect at least one capture method or obtain user agreement for a manual fallback.

## Required tools and binaries

- **Python 3.x** — for bundled helper scripts.
- **git** — for branch, commit, and dirty-state detection.
- **Generic agent tooling** — file read/write, directory listing, shell execution, and search, used according to the environment.

## Recommended tooling (lazy evaluation)

The skill does not require any specific capture tool. It selects a method first, then evaluates tooling for that method only. See [Tooling catalog](TOOLING.md).

| Method | Recommended tooling examples |
|---|---|
| `ui-browser` | Playwright MCP, Stagehand MCP, Puppeteer MCP, project-local Playwright/Cypress |
| `api-http` | curl, HTTPie, httpx, OpenAPI description files |
| `test-runner` | Jest, Vitest, pytest, Go tests |
| `code-snapshot` | git, ripgrep, grep |
| `manual` | none — user provides evidence |

If the selected method's tooling is missing, the skill explains the gap and offers to configure a tool, switch methods, or use manual fallback. It never installs packages or binaries without explicit approval.

## Environment variables

The skill may reference environment variables through config keys (e.g., `username_env`, `password_env` for authentication). It does not require specific variables by default.

## Self-diagnostics contract

At initialization, the skill reports:

- `full` — required capabilities (`git`, `python3`) are present.
- `blocked` — a required capability is missing.

After method selection, the skill may report `degraded` if the selected method lacks recommended tooling, but it remains `blocked` only if the user declines all alternatives.
