# Reference

PR report state management, delta computation, and report generation for `pr-report`.

---

## Configuration

The canonical config location is:

```text
{project-root}/.agents/config/pr-report.yaml
```

On first run, the skill may read legacy user-level config files as fallback sources, but it writes updates to the project-level config. See [CONFIG_PATTERN.md](CONFIG_PATTERN.md).

### Schema

```yaml
# Harness detection: auto | manual
# In auto mode, the skill detects the harness from environment variables and
# configured MCP config paths. It does not assume or hardcode harness names.
harness: auto

# Ordered list of MCP config files to inspect for tokens and endpoints.
# The entries below are examples, not defaults. Configure paths that match your
# environment, or rely on env vars such as MCP_CONFIG_PATH, CLAUDE_MCP_CONFIG,
# KIMI_MCP_CONFIG, GEMINI_MCP_CONFIG, and VSCODE_MCP_CONFIG.
mcp_config_sources:
  - type: example
    path: ${MCP_CONFIG_PATH}
  - type: example
    path: ~/.config/mcp/servers.json
  - type: example
    path: ~/AppData/Roaming/Claude/claude_desktop_config.json

# Explicit token overrides. Values can be literals or ${ENV_VAR} references.
tokens:
  github: ${GITHUB_PERSONAL_ACCESS_TOKEN}
  sonarcloud: ${SONARQUBE_TOKEN}
  jira: ${JIRA_API_TOKEN}

# Provider connection details.
providers:
  github:
    type: github
    api_url: https://api.github.com
    graphql_url: https://api.github.com/graphql
  sonarcloud:
    type: sonarcloud
    base_url: https://sonarcloud.io
    organization: your-org
    project_key: your-org_repo
  jira:
    type: jira
    base_url: https://your-domain.atlassian.net

pr_provider: auto             # auto | github | azure-devops | gitlab | bitbucket | manual
artifact_dir: .agents/context/pr-report

ci:
  provider: auto              # auto | github-actions | azure-pipelines | gitlab-ci | jenkins | none
  auto_fetch: true
  fetch_logs: true

static_analysis:
  provider: auto              # auto | sonarcloud | sonarqube | codeql | semgrep | none
  auto_fetch: true

issue_tracker:
  provider: auto              # auto | jira | github | linear | none

bots:
  sonarqube:
    usernames: [sonarqubecloud]
    source_type: static_analysis
    default_severity: required
  coderabbit:
    usernames: [coderabbitai, coderabbit[bot]]
    source_type: automated_reviewer
    default_severity: recommended
  tate:
    usernames: [T876]
    source_type: hybrid_reviewer
    default_severity: required_to_resolve

notes: []
```

### Field reference

| Key | Description | Default |
|---|---|---|
| `harness` | Harness detection mode. `auto` inspects env vars and configured MCP config paths. | `auto` |
| `mcp_config_sources` | User-configured MCP config files to inspect for tokens. Entries are examples, not defaults. | `[]` |
| `tokens.{provider}` | Explicit token or env-var reference. | extracted from detected MCP config |
| `providers.{provider}` | Connection details for GitHub, SonarCloud, Jira. | inferred from detected MCP config |
| `pr_provider` | PR platform adapter to use. `auto` selects from available providers. | `auto` |
| `artifact_dir` | Directory for state and report files. | `.agents/context/pr-report` |
| `ci.provider` | CI/build adapter. `auto` selects from available providers. | `auto` |
| `ci.auto_fetch` | Whether to fetch CI status automatically. | `true` |
| `ci.fetch_logs` | Whether to summarize failing job logs. | `true` |
| `static_analysis.provider` | Static analysis provider. `auto` selects from available providers. | `auto` |
| `static_analysis.auto_fetch` | Whether to fetch findings automatically. | `true` |
| `issue_tracker.provider` | Issue tracker for scope checks. `auto` selects from available providers. | `auto` |
| `bots` | Bot/human reviewer mappings and source types. | see schema |
| `notes` | Append-only observations. | `[]` |

---

## Resolve PR

Try in order until one succeeds:

1. **Explicit number** — if the user provided digits, use as PR number.
2. **Ticket key** — if input matches `[A-Z][A-Z0-9_]+-\d+`, search open PRs for one whose title or branch contains the key. If multiple match, ask the user.
3. **Current branch** — detect the current branch and search for a PR whose head matches it.
4. **Ask** — ask the user for a PR number or URL.

Detect `owner/repo` from the git remote unless the user overrides it.

---

## State File Specification

Path: `.agents/context/pr-report/{key}/state.md`

```markdown
---
skill: pr-report
version: 1
key: OC-1234
pr_number: 1234
repo: owner/repo
branch: feature/OC-1234-something
base: origin/development
report_status: in-progress
updated_at: 2026-06-26T08:00:00Z
---

# PR Report State: OC-1234

## Phase Checklist
- [x] 1. Resolve PR and load context
- [ ] 2. Fetch PR metadata and changed files
- [ ] 3. Fetch review threads and comments
- [ ] 4. Fetch static analysis
- [ ] 5. Fetch CI / build status
- [ ] 6. Scope check
- [ ] 7. Triage and synthesize issues
- [ ] 8. Render final report

## Current Focus
Phase 2 — fetching PR metadata and changed files.

## Last Completed Action
PR resolved from current branch: owner/repo#1234.

## PR Info
- Number: #1234
- Branch: feature/OC-1234-something
- Base: origin/development
- Ticket: OC-1234

## Session History
| # | Timestamp | Base | Summary |
|---|-----------|------|---------|
| 1 | 2026-06-26T08:00:00Z | origin/development | Initial report. 4 open items. |

## Reviews Tracked
| ID | Reviewer | State | First Seen | Last Updated | Threads Resolved? |
|----|----------|-------|------------|--------------|-------------------|

## Comment History
| ID | Author | Category | First Seen | Last Status | Current Status | Confidence | Resolution | Rebuttal? |
|----|--------|----------|------------|-------------|----------------|------------|------------|-----------|

## Static Analysis Findings
| Key | Severity | Status | First Seen | Last Seen |
|-----|----------|--------|------------|-----------|

## CI / Build Status
| Check | Status | URL | First Seen | Last Seen |
|-------|--------|-----|------------|-----------|

## Triage Decisions
| Issue ID | Sources | Severity | Status | Reason |
|----------|---------|----------|--------|--------|

## Scope Flags
| Comment | Type | Why Flagged | Status |
|---------|------|-------------|--------|

## Files Changed (last known)
| File | Status | First Seen | Last Modified |
|------|--------|------------|---------------|
```

### Section rules

- **Session History:** Append only.
- **Comment History:** Append a new row every time a comment's status changes. Do not delete old rows.
- **Comment status values:** `open`, `resolved`, `uncertain`, `outdated`, `addressed-pending-resolve`, `dismissed-with-reason`, `no-action-needed`.
- **Confidence values:** `high`, `medium`, `low`.
- **Resolution values:** `auto`, `our-response`, `reviewer-resolved`, `outdated`, `uncertain`.
- **Static Analysis Findings:** Update `Last Seen` every iteration. Mark `resolved` if a finding disappears.
- **CI / Build Status:** Update `Last Seen` every iteration. Keep history of status changes.

---

## Delta Computation

For each comment, finding, and check:

| Previous State | Fresh Fetch | Delta Classification |
|----------------|-------------|---------------------|
| Not seen | Open | **New** |
| Not seen | Uncertain | **Unclear status** |
| Open | Resolved | **Resolved since last check** |
| Open | Still open | **Still open** |
| Open | Uncertain | **Unclear status** |
| Our response "Resolved. ..." | Still open | **Addressed by us — pending resolve** |
| Open | Gone / outdated | **Outdated** |
| Passing | Failing | **New failure** |
| Failing | Passing | **Fixed** |

Log the classification in the report and update the state file accordingly.

---

## Report Template

Save the full report to `.agents/context/pr-report/{key}-report.md`.

```markdown
---
skill: pr-report
version: 1
key: OC-1234
pr_number: 1234
repo: owner/repo
branch: feature/OC-1234-something
base: origin/development
report_status: complete
updated_at: 2026-06-26T08:00:00Z
consumed_context: []
---

# PR Report: {pr_title} — Iteration {N}

> Generated: {iso_timestamp} | PR #{pr_number} | Base: {base_ref}

## PR State
- **Review decision:** {CHANGES_REQUESTED | APPROVED | COMMENTED | —}
- **Open items needing action:** {N}
- **CI / build status:** {passing | failing | mixed | unknown}
- **Suggested next step:** {address open items | re-request review from @{reviewer} | wait for reviewer | fix CI}

<!-- STATUS: completed --> ## PR Summary
...

<!-- STATUS: completed --> ## Changed Files
...

<!-- STATUS: completed --> ## CI / Build Status
...

<!-- STATUS: completed --> ## Static Analysis Findings
...

<!-- STATUS: completed --> ## Issues Requiring Action
...

<!-- STATUS: completed --> ## Resolved Since Last Check
...

<!-- STATUS: completed --> ## Threads with Unclear Status
...

<!-- STATUS: completed --> ## Addressed by Us — Pending Resolve
...

<!-- STATUS: completed --> ## Rebuttals Requiring Response
...

<!-- STATUS: completed --> ## Reviewer Status
...

<!-- STATUS: completed --> ## Scope Flags
...

<!-- STATUS: completed --> ## Dismissed / No Action Needed
...
```

## Chat Delivery

After generating the report, deliver this in chat:

```
**PR #{number} — Iteration {N}**
- **Open items needing action:** {N}
- **Top issues to address:**
  - **[severity]** [source] — [one-line summary]
  - **[severity]** [source] — [one-line summary]
  - ... (limit to the most important 3–5 items)
- **Resolved since last check:** {N}
- **Review state:** {CHANGES_REQUESTED | APPROVED | COMMENTED | —} by @{reviewer}
- **CI / build status:** {passing | failing | mixed}
- **Suggested next step:** {address open items | re-request review from @{reviewer} | wait for reviewer | fix CI}
- **Static analysis:** {N} findings ({changed summary})
- **Unclear status:** {N} items
- **Rebuttals:** {N}

Full report: `.agents/context/pr-report/{key}-report.md`
```

If nothing changed:

```
**PR #{number} — Iteration {N}**

No changes since last check ({timestamp}).

- **Open items needing action:** {N}
- **Top issues to address:**
  - **[severity]** [source] — [one-line summary]
  - ... (if any)
- **Review state:** {state}
- **CI / build status:** {status}
- **Suggested next step:** {next step}

Full report: `.agents/context/pr-report/{key}-report.md`
```

---

## Versioning and migration

### Skill version vs schema version

- **Skill version** (`metadata.version` in `SKILL.md`) changes when the skill's behavior, orchestration, or reference semantics change. Bump it when the way the skill interprets config, invokes workers, or synthesizes reports changes.
- **Report/state schema version** (the `version` field in report and state frontmatter) changes when the structure of produced artifacts changes. Bump it when columns, sections, frontmatter fields, or delta classifications are added, removed, or renamed.

A single skill release may bump one, both, or neither. Keep the two version concepts separate in release notes.

### Handling older state and report files

- When loading an existing state or report file, read its `version` field.
- If the version matches the current schema, use the file directly.
- If the version is older but the schema is backward compatible, read what is present and treat missing fields as empty/default.
- If the version is older and the schema is not backward compatible, mark the existing file as stale rather than guessing. Write a new file with the current schema and add a note explaining the migration.
- Never silently discard human-written triage decisions or comment history. Migrate append-only history tables into the new schema when possible.

### Migrating config schema changes

- On first run after a config schema change, load the existing config and validate it against the current schema.
- Map known old keys to new keys automatically when the intent is unambiguous.
- If an old key has no clear equivalent, or if its meaning changed, report the conflict and ask the user rather than guessing.
- Persist the migrated config under the new schema and append a `decision` note recording the migration.

### Marking stale artifacts

When an artifact cannot be migrated safely, rename or move it rather than overwriting it. For example:

```text
.agents/context/pr-report/{key}-report.md
  -> .agents/context/pr-report/archive/{key}-report-v1.md
```

Record the archive path in the new report's frontmatter `archived_artifacts` list or in the state file notes.
