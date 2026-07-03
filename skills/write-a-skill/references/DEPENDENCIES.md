# Dependencies

`write-a-skill` is a meta-level conductor skill. It does not depend on other skills or external services to function.

## Required capabilities

- Read files in the local skills directory.
- Read and write files in `.agents/context/`.
- Spawn focused subagents for delegated analysis and drafting.

## External dependencies

None.

## Existing skills as alternatives

During design, `write-a-skill` evaluates whether a new skill is needed or whether an existing skill, tool, MCP server, prompt template, or script already solves the problem. Existing skills are treated as first-class alternatives, not just inputs.
