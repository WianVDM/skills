# Dependencies

## Required skills

None. `verify-branch` does not require another skill to function.

## Recommended skills

- `artifact-freshness` — used to check whether context reports are fresh before consuming them as advisory context. If unavailable, the skill notes the absence but continues without freshness checks.

## Optional consumed context

The skill may scan `.agents/context/` for reports whose filename or frontmatter matches the current branch or ticket. It consumes these reports as advisory context only; they do not influence the verification verdict.

Any report type may be consumed. The skill does not depend on a specific skill's report.

## Required capabilities

- Read and write the project filesystem (`.agents/config/` and `.agents/context/`).
- Execute shell commands in the project directory.
- Inspect git state (branch, commit, diff, default branch).
- Read project configuration files (e.g., `package.json`, `pyproject.toml`, `go.mod`).

## Required tools

None by default. The skill uses whatever tools the project has configured (test runners, linters, static analyzers, security scanners). The skill ships with adapters for common tools but does not require any specific one.

## Optional runtime dependencies

The following tools are used by built-in adapters and scripts when they are available in the runtime environment:

- `js-yaml` — used by the built-in standards adapters (`yaml-standards`, `markdown-frontmatter`) and the context/state loaders to parse YAML. If `js-yaml` is not installed, the JavaScript loaders fall back to a Python + PyYAML parser.
- `python3` (3.10+) and `PyYAML` — used by the Python context scanners (`scripts/scan-related-context.py`), `scripts/infer-standards.py`, `scripts/detect-gates.py`, and the YAML fallback parser in the standards adapters.
- `artifact-freshness` — used to check whether context reports are fresh before consuming them as advisory context.

Dependency manifests are provided for convenience:

- `package.json` — optional Node dependency `js-yaml`.
- `requirements.txt` — optional Python dependency `PyYAML`.

No additional dependencies are required for the core skill to run.

## Environment variables

The skill may reference environment variables through configured commands or adapter settings. It does not require specific variables by default.
