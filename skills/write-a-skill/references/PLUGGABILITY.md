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

For the canonical implementation, see `skills/detect-project-context/scripts/detect-project-context.py`.

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

The only hardcoded values in this skill are the detection rules and the marker-directory list above.
