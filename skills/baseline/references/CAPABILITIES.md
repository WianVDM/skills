# Capability Detection

The `baseline` skill captures state through many methods. It detects the project type and available tools, then suggests the most relevant methods. The user can override any suggestion.

---

## Baseline method categories

| Category | When to use | Typical evidence |
|----------|-------------|------------------|
| **UI / browser** | The scope is a page, route, component, or visual state. | Screenshots, DOM snapshots, console logs, network logs. |
| **API / HTTP** | The scope is an endpoint, service, or data contract. | Request/response pairs, status codes, response bodies. |
| **Test runner** | The project already has tests that cover the scenario. | Test output, screenshots, logs, coverage. |
| **Code snapshot** | The scope is a module, file set, or architectural state. | File listings, diffs, selected source files. |
| **Manual** | No automation is available or the user wants to provide evidence. | User-provided screenshots, URLs, descriptions. |

---

## Detection order

The skill detects in this order:

1. **Detect project type** — inspect the project to determine what kinds of baselines are relevant.
2. **Identify available methods** — within each relevant category, find available tools and configurations.
3. **Pre-select the best method** — choose the lowest-friction viable option.
4. **Ask the user** when multiple options are viable or when detection is ambiguous.

### Project-type signals

| Project type | Relevant methods |
|--------------|------------------|
| Web frontend (React, Angular, Vue, Svelte, etc.) | UI/browser, test runner, API, code snapshot |
| API/backend service (Node, Python, Go, Java, etc.) | API/HTTP, test runner, code snapshot |
| Library or CLI package | Test runner, code snapshot |
| Static site or documentation | UI/browser, code snapshot |
| Unknown or mixed | Manual, code snapshot, UI/browser if tooling is present |

### UI / browser methods

| Server/Tool | Strengths | Detection |
|-------------|-----------|-----------|
| **Playwright MCP** | Mature, screenshots, navigation, JS evaluation, console logs | Try a simple navigation call |
| **Stagehand MCP** | Natural language browser control | Try a simple navigation call |
| **Puppeteer MCP** | Similar to Playwright | Try a simple navigation call |
| **Browser-tools MCP** | Generic browser actions | Try a simple navigation call |
| **Chrome DevTools MCP** | Direct Chrome control, network logs | Check for Chrome remote debugging endpoint |
| **Project CLI** | `npx playwright`, `npx cypress` if installed | Check installed dependencies and lockfiles |

If no UI automation is available, the skill can offer to guide the user through configuring Playwright MCP. See [PLAYWRIGHT-SETUP.md](PLAYWRIGHT-SETUP.md).

### API / HTTP methods

| Tool | Strengths | Detection |
|------|-----------|-----------|
| **curl** | Universal, no dependencies | Check tool availability |
| **HTTP client MCP** | Structured requests, environment management | Try a simple request |
| **OpenAPI / spec file** | Contract-driven baselines | Look for `openapi.yaml`, `swagger.json`, etc. |
| **Project test suite** | Existing API tests | Look for `*.spec.ts`, `*.test.ts`, etc. |

### Test runner methods

| Tool | Strengths | Detection |
|------|-----------|-----------|
| **Playwright** | End-to-end, screenshots, trace | Check `playwright.config.*` |
| **Cypress** | End-to-end, screenshots | Check `cypress.config.*` |
| **Vitest / Jest** | Unit/integration tests | Check `vitest.config.*`, `jest.config.*` |
| **Storybook** | Component isolation | Check `.storybook/` directory |

### Code snapshot methods

| Approach | Strengths | Detection |
|----------|-----------|-----------|
| **Git tree** | No extra tooling, captures exact file state | Always available in a git repo |
| **Selected files** | Focused on scope | User provides or skill infers from scope |
| **Dependency graph** | Captures module relationships | Use project-specific tools if available |

---

## Selection prompt

When multiple options are available, ask:

> "I found several ways to capture the baseline for `<scope>`:
> 1. UI/browser via Playwright MCP (already configured)
> 2. API/HTTP via curl using the OpenAPI spec
> 3. Existing project test `tests/auth-guard.spec.ts`
> 4. Code snapshot of the affected module
> 5. Manual screenshots or description
> Which should I use?"

Store the choice in `.agents/config/baseline.yaml`.

---

## Fallback behavior

If the selected method fails during execution:

1. Document the failure in the baseline report.
2. Ask the user whether to:
   - Retry with the same method,
   - Try the next best method,
   - Abort.
3. Update notes with the failure and workaround if one is found.
