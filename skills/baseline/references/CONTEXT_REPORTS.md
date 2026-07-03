# Context Reports

The `baseline` skill produces and consumes reports in the shared context directory.

---

## Produced reports

Canonical reports live at:

```text
{project-root}/.agents/context/baseline/{scope}-{branch}.md
{project-root}/.agents/context/baseline/{scope}-{branch}.html   # optional
```

The `{scope}` and `{branch}` placeholders are slugified. For example, a scope of `auth-guard-race-condition` on branch `main` produces:

```text
.agents/context/baseline/auth-guard-race-condition-main.md
```

The `output.naming` config key can change this convention. See [CONFIG_PATTERN.md](CONFIG_PATTERN.md).

### Optional HTML gallery

When `output.default_format` is `html-both`, the skill also writes a self-contained HTML gallery next to the Markdown report. Other skills should read the `.md` report; the HTML file is for human consumption only.

---

## Optional consumed context

Before capturing, the skill may scan `.agents/context/` for reports that help clarify scope, expected behavior, and constraints. It looks for keys matching:

- the current `scope`,
- an inferred ticket key from the scope,
- the current `branch` name.

Common report types consumed:

| Report type | Purpose |
|-------------|---------|
| `debrief` | Ticket understanding and expected behavior. |
| `handoff` | Previous session context and decisions. |
| `plan-next` | Planned next steps and known constraints. |

These reports are optional. The skill must handle their absence gracefully and must not fail if they are missing.

---

## Report schema

Every baseline report must include this frontmatter:

```yaml
---
skill: baseline
version: 3
scope: auth-guard-race-condition
branch: main
commit: abc1234
method: playwright-mcp
consumed_context:
  - .agents/context/debrief/OC-4644.md
  - .agents/context/handoff/OC-4644.md
baselined_at: 2026-06-26T08:42:00Z
type: bug                          # bug | feature | module | route | api | manual
reproducible: true                 # omit for non-bug baselines
artifacts_dir: auth-guard-race-condition-main
summary: "Auth guard redirects to login during token refresh."
---
```

### Field definitions

| Field | Required | Description |
|-------|----------|-------------|
| `skill` | yes | Always `baseline`. |
| `version` | yes | The skill version that produced the report. |
| `scope` | yes | The feature, module, route, bug, or endpoint being baselined. |
| `branch` | yes | The branch being baselined. |
| `commit` | yes | The current commit hash at capture time. |
| `method` | yes | The capture method used. |
| `consumed_context` | no | List of context reports read before capture. |
| `baselined_at` | yes | ISO 8601 timestamp of capture. |
| `type` | yes | Category of baseline: `bug`, `feature`, `module`, `route`, `api`, `manual`. |
| `reproducible` | no | For `bug` baselines, whether the bug was reproduced. |
| `artifacts_dir` | no | Directory containing captured evidence, relative to `.agents/context/baseline/`. |
| `summary` | no | One-sentence synthesis of the baseline. |

### Versioning

The report `version` follows the producing skill's major version. When the skill version changes, report consumers should check the version field and handle older schemas if needed. The skill should document breaking changes in the changelog or migration notes.

---

## Report freshness

A report is stale when any of the following are true:

- The current branch or commit differs from the recorded `branch` or `commit`.
- The recorded `scope` no longer matches the current work.
- The recorded `method` is no longer available or relevant.

When reusing an existing report, the skill should verify freshness and either re-capture or note the staleness explicitly.

---

## Cross-skill consumption

Other skills that read baseline reports should:

1. Read the Markdown report, not the HTML gallery.
2. Trust the `scope`, `branch`, and `commit` fields as the authoritative snapshot context.
3. Treat the `consumed_context` list as a hint for upstream context, not as a dependency.
4. Check `version` if the report format matters to the consumer.

