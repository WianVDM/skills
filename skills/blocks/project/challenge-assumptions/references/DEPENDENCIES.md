# Dependencies

This file lists the tools, binaries, environment variables, and skill dependencies required by `challenge-assumptions`.

## Required tools

| Tool | Purpose |
|---|---|
| `bash` | Executes the deterministic Python script. |
| `read` | Inspect reference files or caller-provided evidence paths when the script is not used directly. |

## Required binaries

| Binary | Version | Purpose |
|---|---|---|
| `python3` | 3.9+ | Runs the deterministic entry point `scripts/challenge-assumptions.py`. |

## Optional binaries

None.

## Environment variables

`challenge-assumptions` does not require any environment variables. It operates entirely on caller-provided JSON input.

## Required skill dependencies

None. `challenge-assumptions` is a deterministic script that does not invoke other skills.

## Recommended skill dependencies

| Skill | Reason |
|---|---|
| `explore-code` | The skill may consume codebase evidence produced by `explore-code` when searching for disproof signals. |
| `context-reports` | The skill may cite its findings in shared context reports; should follow shared report conventions when applicable. |

## Out-of-scope dependencies

- No issue trackers, MCP servers, or external APIs are required.
- No LLM providers or model endpoints are required.
- No filesystem access beyond the deterministic Python script is required by default.
