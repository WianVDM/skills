# Pluggability and detection

`write-a-skill` is a **global** skill. It must work in any project with any agent harness. This document defines how it detects the environment, when it asks the user, and how it falls back when detection is ambiguous.

## Detection rules

1. **Project root:** search upward from the current working directory for a known marker directory:
   - `.agents`
   - `.pi`
   - `agents`
2. **Skills directory:** prefer `{project-root}/{marker}/skills/`. If that does not exist, fall back to common candidates such as `{project-root}/skills/` or `{project-root}/agents/skills/`.
3. **Context directory:** prefer `{project-root}/{marker}/context/`. Fallback: `{project-root}/context/`.
4. **Config directory:** prefer `{project-root}/{marker}/config/`. Fallback: `{project-root}/config/`.

The detection is implemented in [`scripts/detect-project-layout.py`](../scripts/detect-project-layout.py). The script is read-only and deterministic.

## Confidence levels

- **High:** both the skills directory and context directory exist under the detected marker.
- **Medium:** only one of the expected directories exists.
- **Low:** no expected directories exist. The script returns the most likely default paths.

## User-confirmation rules

- **Always confirm** before writing files, even when confidence is high.
- **Ask** when confidence is medium or low.
- **Never** silently create a directory that the user did not approve.
- If the user rejects a detected path, ask for the correct path or abort.

## Fallback behavior

- If no project root is detected, use the current working directory as the root and present the default candidates to the user.
- If the user supplies a custom path, validate that it exists or ask permission to create it.
- If required capabilities are missing (e.g., the subagent harness is unavailable), fail closed with a clear explanation.

## Global portability constraints

Because this skill is global, it must not:

- Hardcode project paths.
- Assume a specific harness, tool name, slash command, or vendor API.
- Rely on project-specific conventions without detection + confirmation.

The only hardcoded values in this skill are the detection rules and the marker-directory list above.
