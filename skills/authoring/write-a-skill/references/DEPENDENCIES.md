# Dependencies and required capabilities

`write-a-skill` is a global, meta-level conductor skill. It delegates deterministic work to standalone building-block skills and uses focused subagents only for tightly coupled design judgment.

The canonical dependency manifest is [`../skills.json`](../skills.json). This document provides the human-readable explanation.

This document follows the dependency taxonomy defined in `docs/skill-standards/fundamentals/architecture/dependencies-and-bundling.md`:

- **Required** — the skill cannot function without this dependency.
- **Recommended** — improves output or experience; the skill runs degraded if it is missing.
- **Optional** — only needed for a side branch or advanced feature.

## Required skills

- **detect-project-context** — project root, skills dir, context dir, and config dir detection.
- **decide-skill-shape** — recommend whether a problem should be a new skill, script, MCP, context file, or mode.
- **audit-skill** — evaluate a skill against the fundamentals rubric.
- **validate-skill-frontmatter** — validate `SKILL.md` frontmatter against the JSON schema.
- **review-skill** — audit an existing skill and optionally apply remediation changes.
- **eval-format** — shared `evals/evals.json` schema and evaluation conventions.
- **worker-contract** — shared subagent return contract, forbidden actions, and scope boundaries used when composing worker prompts.
- **context-reports** — shared context-report conventions, schema, freshness rules, and missing-report handling.
- **parse-skill-frontmatter** — extract canonical frontmatter fields from a `SKILL.md` file (used by several building blocks above).

## Recommended skills

- **list-available-skills** — discover skills already available in the project and user scope. Without it, the alternatives report is limited to what the conductor can find directly.
- **search-skills-registry** — find third-party skills in configured registries. Without it, the skill cannot check whether a similar third-party skill already exists.
- **detect-skill-overlap** — flag when a skill duplicates or could be extracted from an existing building block. Without it, the alternatives and colocation phases lack overlap analysis.
- **install-skill** — install a skill from a local path or archive URL after confirmation. Without it, the conductor can draft files but cannot install skills on the user's behalf.
- **run-trigger-evals** — generate `evals/evals.json` for model-invoked skills. Without it, the conductor can ask the user to write evals manually or skip them.

## Optional skills

- **prototype** — only used when the user explicitly asks to prototype a UI variation before drafting a skill. Not on the main path.

## Required harness capabilities

- **File read** — to inspect skill files, context reports, and references.
- **File write** — to write context reports and, after user confirmation, skill files.
- **File edit** — to update existing reports and decision logs.
- **Directory listing** — to discover existing skills and project structure.
- **Script execution** — to run deterministic helpers in building-block skill directories.
- **Subagent spawning** — for delegated analysis, design, review, and drafting.
- **Search** — to locate files and symbols across the project.

## Required binaries

- **Python 3.x** — to execute the bundled scripts in building-block skills.

## External dependencies

- Network access is required only for `search-skills-registry` and for the optional standards-initialization fetch.
- Subagents may use web search to research alternatives, but the core skill does not require it.

## Tool categories

`write-a-skill` may consume skills that depend on any of the following tool categories. The conductor must teach authors to design capability-first and consider every category before hardcoding an adapter:

| Category | Examples |
|---|---|
| **Provider-specific adapters** | GitHub PR adapter, SonarCloud adapter, Jira adapter |
| **MCP tools / servers** | `github_get_pull_request_reviews`, SonarQube MCP, Jira MCP |
| **Native binaries** | `gh`, `git`, `curl`, `jq` |
| **Direct APIs** | Provider REST or GraphQL endpoints |
| **Harness tools** | Built-in browser, file system, search, shell |
| **Manual fallback** | User input, CSV, markdown files |

A drafted skill must not treat its own adapters as the only source for a capability.

## Environment variables

- None. This skill does not read environment variables directly.
- If the user configures a network proxy or token for the optional standards fetch, the harness or underlying HTTP client handles it; the skill itself does not read those variables.

## Shipped schema fallback

`audit-skill` ships a portable copy of `skill-frontmatter.schema.json` in `audit-skill/references/`. `validate-skill-frontmatter` falls back to this copy when the canonical `docs/skill-standards/schemas/skill-frontmatter.schema.json` is unavailable. This lets `write-a-skill` and its dependencies run in workspaces that do not include the full standards wiki.

## Consumed references

This skill consumes the following canonical standards and guidance documents:

- [references/FUNDAMENTALS.md](FUNDAMENTALS.md) — condensed skill fundamentals.
- [references/PATTERN_HINTS.md](PATTERN_HINTS.md) — condensed Layer 2 pattern decision rules.
- [references/PLUGGABILITY.md](PLUGGABILITY.md) — detection rules and global portability constraints.
- [references/STATE_SCHEMA.md](STATE_SCHEMA.md) — artifact schemas.
- [references/BRANCH_WORKFLOWS.md](BRANCH_WORKFLOWS.md) — detailed per-branch workflows.
- [references/WORKER_CONTRACT.md](WORKER_CONTRACT.md) — standard subagent return contract.
- [references/GUIDE_SCRIPT_CURATION.md](GUIDE_SCRIPT_CURATION.md) — when to use scripts.
- [references/GUIDE_EXAMPLES.md](GUIDE_EXAMPLES.md) — example skill structures.
- [references/EVAL.md](EVAL.md) — trigger and behavioral evals.
- [README.md](../README.md) — how to invoke the skill and a short directory layout.
- [references/GOVERNANCE.md](GOVERNANCE.md) — versioning, migration history, review cadence, and maintenance notes.

## Assumed project conventions

- The project may contain a marker directory such as `.agents`, `.pi`, or `agents` that holds `skills/`, `context/`, and `config/`.
- If no marker directory is found, the skill falls back to detection and asks the user for confirmation.
- This assumption is documented in [references/PLUGGABILITY.md](PLUGGABILITY.md).

## Existing skills as alternatives

During design, `write-a-skill` evaluates whether a new skill is needed or whether an existing skill, tool, MCP server, prompt template, or script already solves the problem. Existing skills are treated as first-class alternatives, not just inputs.
