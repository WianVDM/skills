# Dependencies

This file lists the tools, binaries, environment variables, and skill dependencies required by `explore-code`.

## Required harness tools

| Tool | Purpose |
|---|---|
| `read` | Read discovered files to confirm existence and summarize content. |
| `ffgrep` | Fast content search across the codebase for keywords and patterns. |
| `fffind` | Fuzzy/glob file discovery for finding tests, ADRs, and comparable files. |
| `bash` | Fallback to `rg`/`find` when harness tools are unavailable or for directory traversal. |

## Recommended harness tools

| Tool | Purpose |
|---|---|
| `find` | Alternative path discovery in environments where `fffind` is unavailable. |
| `grep` | Generic fallback text search when `ffgrep` is unavailable. |

## Required binaries

| Binary | Version | Purpose |
|---|---|---|
| `python3` | 3.9+ | Runs the deterministic entry point `scripts/explore-code.py`. |

## Optional binaries

| Binary | Purpose |
|---|---|
| `rg` (ripgrep) | Fast fallback content search when `ffgrep` is unavailable. |
| `find` (POSIX/MSYS) | Directory traversal fallback. |

## Environment variables

`explore-code` does not require any environment variables. It uses the caller-provided `workspace` and project root to scope searches.

## Required skill dependencies

| Skill | Reason |
|---|---|
| `worker-contract` | The skill returns a structured result to conductors and must follow the shared worker/subagent return format, forbidden actions, and scope boundaries. |

## Recommended skill dependencies

| Skill | Reason |
|---|---|
| `context-reports` | Evidence produced by this skill can be cited in shared context reports; should follow shared report conventions when applicable. |

## Out-of-scope dependencies

- No issue trackers, MCP servers, or external APIs are required.
- No LLM providers or model endpoints are required.
