# Tooling catalog

The `baseline` skill is method-agnostic. It does not require any specific vendor tool, but some capture methods work best when the project already has matching tooling.

This catalog lists common tools and configurations for each method. The skill evaluates tooling **lazily**: it only checks the catalog entry relevant to the method selected for the current baseline.

## Method: `ui-browser`

Use for pages, routes, components, or visual interactions.

### Detectable signals

- `playwright.config.ts/js/mjs` or `@playwright/test` dependency.
- `cypress.config.js/ts` or `cypress` dependency.
- `puppeteer` or `puppeteer-core` dependency.
- An MCP server with `playwright`, `stagehand`, `puppeteer`, `browser-tools`, or `chrome-devtools` in its config.

### Common options

| Tool | When to use | Config surface |
|------|-------------|--------------|
| Playwright MCP | Harness provides a Playwright MCP server. | `{config_dir}/mcp.json` or harness-native MCP config. |
| Stagehand MCP | AI-driven browser automation via MCP. | `{config_dir}/mcp.json` or harness-native MCP config. |
| Puppeteer MCP | Direct Chrome DevTools Protocol access. | `{config_dir}/mcp.json` or harness-native MCP config. |
| Project-local Playwright | Existing test suite already uses Playwright. | `playwright.config.*` |
| Project-local Cypress | Existing test suite already uses Cypress. | `cypress.config.*` |

### Manual fallback

Provide screenshots, DOM snapshots, or URLs supplied by the user.

## Method: `api-http`

Use for endpoints, services, or data contracts.

### Detectable signals

- `curl`, `http`, `httpx`, or `wget` in PATH.
- `openapi.json`, `openapi.yaml`, `swagger.json`, or `swagger.yaml` in the project root.
- Existing API test files.

### Common options

| Tool | When to use | Config surface |
|------|-------------|--------------|
| curl | Lightweight check, available almost everywhere. | No config needed. |
| HTTPie / httpx | Richer HTTP client output. | No config needed. |
| OpenAPI description file | Documented contract exists. | `openapi.json` / `openapi.yaml` |

### Manual fallback

User provides request/response pairs or curl commands.

## Method: `test-runner`

Use when existing tests cover the scoped scenario.

### Detectable signals

- `jest.config.*`, `vitest.config.*`, `playwright.config.*`, `cypress.config.*`.
- `pytest.ini`, `pyproject.toml` with pytest, or `tox.ini`.
- `*_test.go` files and `go.mod`.

### Common options

| Tool | When to use | Config surface |
|------|-------------|--------------|
| Jest / Vitest | JavaScript/TypeScript unit or integration tests. | `jest.config.*` / `vitest.config.*` |
| Playwright tests | End-to-end tests already cover the feature. | `playwright.config.*` |
| pytest | Python project with test coverage. | `pytest.ini` / `pyproject.toml` |
| Go tests | Go project with tests. | `go test` |

### Manual fallback

Run the test command manually and provide the output.

## Method: `code-snapshot`

Use for modules, file sets, or architectural state.

### Detectable signals

- Git repository with source files matching the scope.
- Common source extensions in the project.

### Common options

| Tool | When to use | Config surface |
|------|-------------|--------------|
| git | Required by the skill itself; sufficient for file listings and diffs. | `.git/` |
| ripgrep / grep | Search for symbols or references. | No config needed. |

### Manual fallback

User provides the relevant files or a file listing.

## Method: `manual`

Always available. The user provides evidence directly.

## Configuration guidance rules

- The skill may suggest a tool from this catalog, but it must not require a specific vendor.
- If the skill generates a config file (e.g., a minimal Playwright config), it must ask for explicit confirmation first.
- The skill must not run package installers (`npm install`, `pip install`, etc.) without explicit approval.
- The skill must not silently degrade to `manual` if a better method was selected; it must explain the gap and ask.

## Persisting tooling preferences

When the user chooses a tooling path for a method, the skill records it in `{config_dir}/baseline.yaml` under `tooling.{method}` so the same question is not repeated every run.
