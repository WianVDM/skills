# Dependencies and required capabilities

`write-a-skill` is a global, meta-level conductor skill. It does not depend on other skills to function, but it does depend on specific harness capabilities and project conventions.

## Required harness capabilities

- **Read files** in the local skills directory and context directory.
- **Write files** in the detected context directory and, after confirmation, in the detected skills directory.
- **Spawn focused subagents** for delegated analysis, design, review, and drafting.
- **Run scripts** in the skill directory, specifically `scripts/detect-project-layout.py`.
- **List directories** using `bash` or equivalent to discover existing skills and project structure.
- **Python 3.x** to execute `scripts/detect-project-layout.py`.

## External dependencies

None. The skill performs no network calls, API requests, or external service access by default. Subagents may use `web_search` to research alternatives, but the core skill does not require it.

## Consumed references

This skill consumes the following canonical standards and guidance documents:

- [references/AUDIT_RUBRIC.md](references/AUDIT_RUBRIC.md) — the A–K criteria used to review skills.
- [references/PLUGGABILITY.md](references/PLUGGABILITY.md) — detection rules and global portability constraints.
- [references/SELF_AUDIT_CHECKLIST.md](references/SELF_AUDIT_CHECKLIST.md) — pre-draft fundamentals check.
- [references/STATE_SCHEMA.md](references/STATE_SCHEMA.md) — artifact schemas.
- [references/CONTEXT_REPORTS.md](references/CONTEXT_REPORTS.md) — report schemas and freshness rules.
- [references/WORKER_CONTRACT.md](references/WORKER_CONTRACT.md) — standard subagent return contract.
- [references/GUIDE_SCRIPT_CURATION.md](references/GUIDE_SCRIPT_CURATION.md) — when to use scripts.
- [references/GUIDE_EXAMPLES.md](references/GUIDE_EXAMPLES.md) — example skill structures.
- [references/EVAL.md](references/EVAL.md) — trigger and behavioral evals.
- [references/MAINTENANCE.md](references/MAINTENANCE.md) — versioning and review cadence.

## Assumed project conventions

- The project may contain a `.agents/` directory that holds `skills/`, `context/`, and `config/`.
- If the convention is not found, the skill falls back to detection and asks the user for confirmation.
- This assumption is documented in [references/PLUGGABILITY.md](references/PLUGGABILITY.md).

## Existing skills as alternatives

During design, `write-a-skill` evaluates whether a new skill is needed or whether an existing skill, tool, MCP server, prompt template, or script already solves the problem. Existing skills are treated as first-class alternatives, not just inputs.
