# Capability Detection

The skill detects the project type and available capture methods, then suggests the most viable one. The user can override any suggestion.

---

## Method categories

| Category | When to use | Typical evidence |
|----------|-------------|------------------|
| **UI / browser** | Page, route, component, or visual state. | Screenshots, DOM snapshots, console logs, network logs. |
| **API / HTTP** | Endpoint, service, or data contract. | Request/response pairs, status codes, response bodies. |
| **Test runner** | Existing tests cover the scenario. | Test output, screenshots, logs, traces. |
| **Code snapshot** | Module, file set, or architectural state. | File listings, diffs, selected source files. |
| **Manual** | No automation or user wants to provide evidence. | User-provided screenshots, URLs, descriptions. |

## Detection order

1. **Detect project type** — determine what kinds of baselines are relevant.
2. **Identify available methods** — find tools and configurations for each relevant category.
3. **Pre-select the best method** — choose the lowest-friction viable option.
4. **Ask the user** when multiple options are viable or detection is ambiguous.

### Project-type signals

| Project type | Relevant methods |
|--------------|------------------|
| Web frontend | UI/browser, test runner, API, code snapshot |
| API/backend service | API/HTTP, test runner, code snapshot |
| Library or CLI package | Test runner, code snapshot |
| Static site or documentation | UI/browser, code snapshot |
| Unknown or mixed | Manual, code snapshot, UI/browser if tooling is present |

### What is detected

- **UI/browser:** browser automation dependencies, MCP configs, locally installed binaries.
- **API/HTTP:** HTTP clients, MCP servers, API description files, existing API tests.
- **Test runner:** test configs, test dependencies, test files.
- **Code snapshot:** git repository, source files matching the scope, dependency/module tools.

If the selected method fails, document the failure, ask whether to retry, try the next best method, or abort, and update notes with any workaround.
