# Dependencies and required capabilities

`write-a-skill` is a global, meta-level conductor skill. It delegates deterministic work to standalone building-block skills and uses focused subagents only for tightly coupled design judgment.

## Required building-block skills

- **detect-project-context** — project root, skills dir, context dir, and config dir detection.
- **list-available-skills** — discover skills already available in the project and user scope.
- **search-skills-registry** — find third-party skills in configured registries.
- **install-skill** — install a skill from a local path or archive URL after confirmation.
- **decide-skill-shape** — recommend whether a problem should be a new skill, script, MCP, context file, or mode.
- **audit-skill** — evaluate a skill against the fundamentals rubric.
- **validate-skill-frontmatter** — validate `SKILL.md` frontmatter against the JSON schema.
- **review-skill** — audit an existing skill and optionally apply remediation changes.
- **run-trigger-evals** — generate `evals/evals.json` for model-invoked skills.
- **eval-format** — shared `evals/evals.json` schema and evaluation conventions.
- **worker-contract** — shared subagent return contract, forbidden actions, and scope boundaries used when composing worker prompts.
- **context-reports** — shared context-report conventions, schema, freshness rules, and missing-report handling.
- **parse-skill-frontmatter** — extract canonical frontmatter fields from a `SKILL.md` file (used by several building blocks above).

## Required harness capabilities

- **Read files** in the local skills directory and context directory.
- **Write files** in the detected context directory and, after confirmation, in the detected skills directory.
- **Spawn focused subagents** for delegated analysis, design, review, and drafting.
- **Run scripts** in the building-block skill directories.
- **List directories** using `bash` or equivalent to discover existing skills and project structure.
- **Python 3.x** to execute the bundled scripts.

## External dependencies

- Network access is required only for `search-skills-registry` and for the optional standards-initialization fetch.
- Subagents may use `web_search` to research alternatives, but the core skill does not require it.

## Consumed references

This skill consumes the following canonical standards and guidance documents:

- [references/FUNDAMENTALS.md](references/FUNDAMENTALS.md) — condensed skill fundamentals.
- [references/PATTERN_HINTS.md](references/PATTERN_HINTS.md) — condensed Layer 2 pattern decision rules.
- [references/PLUGGABILITY.md](references/PLUGGABILITY.md) — detection rules and global portability constraints.
- [references/STATE_SCHEMA.md](references/STATE_SCHEMA.md) — artifact schemas.
- [references/BRANCH_WORKFLOWS.md](references/BRANCH_WORKFLOWS.md) — detailed per-branch workflows.
- [references/WORKER_CONTRACT.md](references/WORKER_CONTRACT.md) — standard subagent return contract.
- [references/GUIDE_SCRIPT_CURATION.md](references/GUIDE_SCRIPT_CURATION.md) — when to use scripts.
- [references/GUIDE_EXAMPLES.md](references/GUIDE_EXAMPLES.md) — example skill structures.
- [references/EVAL.md](references/EVAL.md) — trigger and behavioral evals.
- [README.md](../README.md) — versioning, review cadence, and maintenance notes.

## Assumed project conventions

- The project may contain a `.agents/` directory that holds `skills/`, `context/`, and `config/`.
- If the convention is not found, the skill falls back to detection and asks the user for confirmation.
- This assumption is documented in [references/PLUGGABILITY.md](references/PLUGGABILITY.md).

## Existing skills as alternatives

During design, `write-a-skill` evaluates whether a new skill is needed or whether an existing skill, tool, MCP server, prompt template, or script already solves the problem. Existing skills are treated as first-class alternatives, not just inputs.
