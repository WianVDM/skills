# Dependencies

## Declared dependencies

Canonical dependency declarations live in `SKILL.md` frontmatter (`depends`). The sections below summarize them for human readers.

## Required skills

- `context-reports` — for shared state/report conventions and the canonical context-report directory layout.

## Recommended skills

None required. `checkpoint` is a standalone building block.

## Optional consumed context

`checkpoint` does not consume reports produced by other skills. It writes a single markdown state file that other skills or conductors may read.

## Required scripts

- `_frontmatter` — shared frontmatter parser. The `checkpoint` script imports the parser from `skills/workflow/debrief/scripts/_frontmatter.py` at runtime.

## Required tools and binaries

- **Python 3.x** — for the bundled helper script.
- **Generic agent tooling** — file read/write, used according to the environment.

## Recommended tooling (lazy evaluation)

- **PyYAML** — enables strict YAML frontmatter parsing. If unavailable, `checkpoint` falls back to the simple YAML-like parser in `_frontmatter.py`.

## Environment variables

`checkpoint` does not require specific environment variables.

## Related conventions

- Callers that coordinate subagents should follow the `worker-contract` conventions for return values and scope boundaries. `checkpoint` itself does not invoke subagents, so `worker-contract` is a caller-side convention rather than a runtime dependency.

## Self-diagnostics contract

At initialization, the script reports:

- `full` — required capabilities (Python 3.x) are present.
- `blocked` — a required capability is missing (e.g., Python interpreter not available).

The script fails closed on missing or corrupt state files when `update` or `resume` is requested without `create`.
