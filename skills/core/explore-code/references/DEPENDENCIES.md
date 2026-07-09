# Dependencies

This file lists the tools, binaries, environment variables, and skill dependencies required by `explore-code`.

## Required tools

| Tool | Purpose |
|---|---|
| `bash` | Executes the deterministic Python script and any `rg` subprocess calls. |

## Required binaries

| Binary | Version | Purpose |
|---|---|---|
| `python3` | 3.9+ | Runs the deterministic entry point `scripts/explore-code.py`. |

## Recommended binaries

| Binary | Purpose |
|---|---|
| `rg` (ripgrep) | Fast content search across the codebase when available. The script falls back to Python's built-in directory walk if `rg` is missing. |

## Optional binaries

| Binary | Purpose |
|---|---|
| `find` (POSIX/MSYS) | Alternative directory traversal when the Python fallback is insufficient. |

## Environment variables

`explore-code` does not require any environment variables. It uses the caller-provided `workspace` and `project_root` to scope searches.

## Required skill dependencies

None. `explore-code` is a deterministic script that does not invoke other skills.

## Recommended skill dependencies

| Skill | Reason |
|---|---|
| `context-reports` | Evidence produced by this skill can be cited in shared context reports; should follow shared report conventions when applicable. |

## Out-of-scope dependencies

- No issue trackers, MCP servers, or external APIs are required.
- No LLM providers or model endpoints are required.
