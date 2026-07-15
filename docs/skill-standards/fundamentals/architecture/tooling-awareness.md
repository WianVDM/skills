# Tooling awareness

A skill must be **capability-first and tool-aware**, not adapter-first and closed-loop. For every capability it needs, the skill must discover the tools that could fulfill it, select the best available one, and disclose the choice.

## Capabilities come first

A **capability** is an outcome the skill needs, not a specific tool. Examples:

- Obtain full top-level review bodies for a pull request.
- Fetch static-analysis findings for a commit or branch.
- Resolve ticket scope and acceptance criteria.
- Capture the current UI state.

An **adapter**, **MCP tool**, **native binary**, **direct API**, **harness tool**, or **manual fallback** is one possible implementation of that capability. The skill must not confuse the implementation with the outcome.

## Tool categories

A skill should consider the full tool catalog, not only its own adapters:

| Category | Examples |
|---|---|
| **Provider-specific adapters** | GitHub PR adapter, SonarCloud adapter, Jira adapter |
| **MCP tools / servers** | `github_get_pull_request_reviews`, SonarQube MCP, Jira MCP |
| **Native binaries** | `gh`, `git`, `curl`, `jq` |
| **Direct APIs** | Provider REST or GraphQL endpoints called directly |
| **Harness tools** | Built-in browser, file system, search, shell |
| **Shared storage adapters** | `chainlog` file adapter, graph-backed chainlog adapter |
| **Manual fallback** | User input, CSV, markdown files |

## Tool discovery

Tool discovery is part of the skill's initialization or first collection phase. Before committing to a source, the skill should:

1. Read project config (`.mcp.json`, `.agents/config/`, `.env` conventions) for configured MCP servers and tools.
2. Query the MCP gateway or harness for available tools.
3. Check configured skill adapters and native binaries.
4. Record detected tools per capability in state or the report.

Discovery is not a one-time setup cost. The skill may discover new tools on each run because project configuration changes.

## Tool selection hierarchy

For each capability, prefer the tool that:

1. Returns the most **complete**, **authoritative**, and **reliable** data.
2. Is already **configured and working**.
3. Requires **no additional user setup**.
4. Provides **direct evidence** rather than inference or reconstruction.
5. **Fits the skill's contract** without leaking implementation details.

Provider-specific adapters are one valid option in this hierarchy. They should win when they are genuinely the best source for a project, not simply because they exist.

## Disclosure and user-consented degradation

If the skill uses a weaker tool or skips a capability, it must tell the user:

- What tool was used.
- Why it was chosen.
- What better tool was available but unused.
- What impact the choice has on the output.
- How to override the choice now or persist a different preference.

The user must be able to accept the degraded source knowingly or ask the skill to use the better tool instead.

### Degradation disclosure template

Use a form like this in chat summaries or reports:

> I used `{tool}` for `{capability}` because `{reason}`. A better source, `{better_tool}`, is configured and available. If you want me to fetch from `{better_tool}` instead, confirm and I will rerun that section. Otherwise the current section may be degraded.

## Failure mode: adapter tunnel vision

A skill has **adapter tunnel vision** when it treats its own built-in adapters, scripts, or preferred paths as the only way to fulfill a capability, ignoring better tools that are already configured or available.

**Symptoms:**

- Reconstructing data from partial outputs instead of using a better tool.
- Declaring a source "unavailable" when an MCP server or native tool could reach it.
- Recording limitations and moving on without suggesting alternatives.
- Marking a section complete while a better tool sits unused.

**Cure:**

Design each capability step as "what outcome do I need?" first, then "which available tool gives the best result?" Route through the best tool and disclose the choice.

## Related documents

- [`dependencies-and-bundling.md`](./dependencies-and-bundling.md) — dependency taxonomy, including tools and the self-diagnostics contract.
- [`common-mistakes/`](../core/common-mistakes/) — adapter tunnel vision as a failure mode.
- [`evaluation.md`](./evaluation.md) — testing tool selection and degradation disclosure.
- [`../patterns/building-block.md`](../../patterns/building-block.md) — reusable skills that expose capabilities.
- [`../patterns/conductor.md`](../../patterns/conductor.md) — coordinating tools and capabilities.

## Research basis

See [SOURCES.md](../../reference/sources.md).
