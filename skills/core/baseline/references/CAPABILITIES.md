# Capability Detection

The skill detects the project type and available capture methods, then suggests the most viable one. Tooling is evaluated **lazily**: only the catalog entry relevant to the selected method is checked. The user can override any suggestion.

---

## Method categories

| Category | Canonical method name | When to use | Typical evidence |
|----------|----------------------|-------------|------------------|
| **UI / browser** | `ui-browser` | Page, route, component, or visual state. | Screenshots, DOM snapshots, console logs, network logs. |
| **API / HTTP** | `api-http` | Endpoint, service, or data contract. | Request/response pairs, status codes, response bodies. |
| **Test runner** | `test-runner` | Existing tests cover the scenario. | Test output, screenshots, logs, traces. |
| **Code snapshot** | `code-snapshot` | Module, file set, or architectural state. | File listings, diffs, selected source files. |
| **Manual** | `manual` | No automation or user wants to provide evidence. | User-provided screenshots, URLs, descriptions. |

## Detection order

1. **Detect project type** — determine what kinds of baselines are relevant.
2. **Identify available methods** — find tools and configurations for each relevant category at a high level.
3. **Pre-select the best method** — choose the lowest-friction viable option based on scope and project type.
4. **Evaluate tooling for the selected method** — check only the catalog entry relevant to the selected method.
5. **Ask the user** if tooling is missing, if multiple options are viable, or if detection is ambiguous.

### Project-type signals

| Project type | Relevant methods |
|--------------|------------------|
| Web frontend | `ui-browser`, `test-runner`, `api-http`, `code-snapshot` |
| API/backend service | `api-http`, `test-runner`, `code-snapshot` |
| Library or CLI package | `test-runner`, `code-snapshot` |
| Static site or documentation | `ui-browser`, `code-snapshot` |
| Unknown or mixed | `manual`, `code-snapshot`, `ui-browser` if tooling is present |

### What is detected (per method, on demand)

- **`ui-browser`:** browser automation dependencies, MCP configs, locally installed binaries. See [Tooling catalog](TOOLING.md).
- **`api-http`:** HTTP clients, API description files, existing API tests. See [Tooling catalog](TOOLING.md).
- **`test-runner`:** test configs, test dependencies, test files. See [Tooling catalog](TOOLING.md).
- **`code-snapshot`:** git repository, source files matching the scope, dependency/module tools. See [Tooling catalog](TOOLING.md).
- **`manual`:** always available.

### Handling missing tooling

When the selected method lacks tooling:

1. Explain the gap for that method only.
2. Offer to configure a recommended tool, switch to an alternative method, or use manual fallback.
3. Ask for explicit confirmation before generating any config file.
4. Record the chosen tooling path in `{config_dir}/baseline.yaml` after confirmation.

If the user declines all alternatives, the skill stops and reports `blocked` for that method.

If the selected method fails, document the failure, ask whether to retry, try the next best method, or abort, and update notes with any workaround.

### Source-file detection limitations

The bundled `detect-baseline-method.py` script looks for source files up to a bounded depth (currently three directory levels below the project root) to keep scans cheap and deterministic. Deeply nested repositories with source files more than three levels below the root may be reported as `code-snapshot: unavailable` even though source exists. In such cases, the skill should either invoke a deeper search explicitly, ask the user to confirm the target files, or treat the limitation as documented and select another method.
