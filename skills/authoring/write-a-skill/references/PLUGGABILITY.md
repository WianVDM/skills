# Pluggability and detection

`write-a-skill` is a global skill. It must work in any project with any agent harness. This document is a short reference; the detection rules live in the `detect-project-context` building block.

## Detection rules

1. **Project root:** search upward from the current working directory for a known marker directory:
   - `.agents`
   - `.pi`
   - `agents`
2. **Skills directory:** prefer `{project-root}/{marker}/skills/`. Fallback: `{project-root}/skills/`, `{project-root}/agents/skills/`.
3. **Context directory:** prefer `{project-root}/{marker}/context/`. Fallback: `{project-root}/context/`.
4. **Config directory:** prefer `{project-root}/{marker}/config/`. Fallback: `{project-root}/config/`.

For the canonical implementation, see the `detect-project-context` skill.

## Confidence levels

- **High:** both the skills directory and context directory exist under the detected marker.
- **Medium:** only one of the expected directories exists.
- **Low:** no expected directories exist. The detector returns the most likely default paths.

## User-confirmation rules

- Always confirm before writing files, even when confidence is high.
- Ask when confidence is medium or low.
- Never silently create a directory that the user did not approve.
- If the user rejects a detected path, ask for the correct path or abort.

## Global portability constraints

Because this skill is global, it must not:

- Hardcode project paths.
- Assume a specific harness, tool name, slash command, or vendor API.
- Rely on project-specific conventions without detection + confirmation.

The only hardcoded project-level values are the detection rules, the marker-directory list above, and the skill's own config filename (which the harness uses to locate this skill's configuration). All other paths and conventions must come from detection, configuration, or user confirmation.

## Degradation

- If the harness cannot spawn subagents, the conductor must run the same phases inline and ask the user the questions a worker would have returned.
- If the harness cannot load `config.yaml`, the skill uses `detect-project-context` defaults and asks the user to confirm.
- If the harness cannot fetch external standards, the skill falls back to the embedded `references/FUNDAMENTALS.md` and `references/PATTERN_HINTS.md`.
- If the project context cannot be detected, the skill fails closed and explains what is missing.
