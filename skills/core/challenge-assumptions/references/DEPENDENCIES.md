# Dependencies

This file lists the tools, binaries, environment variables, and skill dependencies required by `challenge-assumptions`.

## Required harness tools

| Tool | Purpose |
|---|---|
| `read` | Read the `SKILL.md` and reference files. |
| `ffgrep` | Search codebase evidence for contradiction signals when the caller provides file paths. |
| `fffind` | Locate evidence files referenced by path when the caller provides them. |
| `bash` | Execute the deterministic Python script. |

## Recommended harness tools

| Tool | Purpose |
|---|---|
| `grep` | Generic fallback text search when `ffgrep` is unavailable. |
| `find` | Alternative path discovery when `fffind` is unavailable. |

## Required binaries

| Binary | Version | Purpose |
|---|---|---|
| `python3` | 3.9+ | Runs the deterministic entry point `scripts/challenge-assumptions.py`. |

## Optional binaries

None.

## Environment variables

`challenge-assumptions` does not require any environment variables. It operates entirely on caller-provided JSON input.

## Required skill dependencies

| Skill | Reason |
|---|---|
| `context-reports` | The skill may cite its findings in shared context reports; it follows the shared report conventions when applicable. |
| `worker-contract` | The skill returns a structured result to conductors and must follow the shared worker/subagent return format, forbidden actions, and scope boundaries. |
| `explore-code` | The skill may consume codebase evidence produced by `explore-code` when searching for disproof signals. |

## Recommended skill dependencies

None.

## Out-of-scope dependencies

- No issue trackers, MCP servers, or external APIs are required.
- No LLM providers or model endpoints are required.
- No filesystem access beyond the deterministic Python script is required by default.
