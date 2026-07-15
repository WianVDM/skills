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
- If the harness cannot fetch external standards, the skill falls back to the embedded `references/FUNDAMENTALS.md` and `references/PATTERN_HINTS.md` and must use the degraded-mode warning template below.
- If the project context cannot be detected, the skill fails closed and explains what is missing.
- If `standards_path` is configured but the directory is missing, the skill warns and falls back to embedded docs.
- If `capability_index_path` is configured but the file is missing, the skill searches for `.agents/skill-capability-index.json`, then `docs/skill-capability-index.json`, and finally builds a description-level index from the repository files. The user is warned and can regenerate the index if needed.

## Capability index discovery

`write-a-skill` and its building blocks use the machine-readable capability index for overlap detection. The index path is resolved lazily:

1. Configured `capability_index_path` in `write-a-skill.yaml`.
2. Project-local override at `.agents/skill-capability-index.json`.
3. Bundle default at `docs/skill-capability-index.json`.
4. Build a fresh index from the repository files as a fallback.

If the index is stale or missing, the skill warns the user and continues in degraded mode. It never fails silently.

## Degraded-mode warning template

Whenever `write-a-skill` falls back to embedded guidance or skips a standards-backed check, present the warning using this exact template and record the user's choice in the decision log:

> **Degraded mode:** The canonical skill-standards docs are not available at `{standards_path}`. Some checks will use the embedded fallback guidance in `references/FUNDAMENTALS.md` and `references/PATTERN_HINTS.md`, which may be older or less complete. You can fetch the latest standards from `github.com/wianvdm/skills` or set `standards_path` to a local copy.
>
> - **Better option:** Fetch or point to the canonical standards.
> - **Current fallback:** Use embedded guidance.
> - **Missing checks:** Pattern-to-canonical mapping, full rubric cross-references, and some overlap-detection heuristics may be reduced.
>
> Do you want to proceed with the fallback, fetch the standards, or stop?

Use this template consistently across the `initialize`, `create`, and `change` branches. Never silently fall back without telling the user.
