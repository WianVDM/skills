---
name: detect-project-context
description: Detect the project root, skill/context/config directories, and the skill-standards path for any workspace.
invocation: model-invoked
---

# detect-project-context

Tool building block: answer where project-level directories live so no skill hardcodes paths.

## Contract

Read-only and deterministic. Given a start directory, return the project root, marker, confidence, and recommended directories as structured JSON. Never write, never prompt.

## Operations

- `scripts/detect-project-context.py` — root and directory detection.
- `scripts/resolve-standards-path.py` — canonical skill-standards path (cli → config → marker → project defaults → bundle), with degraded-mode disclosure.

## In scope

- Upward marker search (`.agents`, `.pi`, harness markers), bounded by the VCS root.
- Candidate ranking; existing directories win.
- Confidence reporting, with a `note` when the answer is weakened.

## Out of scope

- Writing or creating directories.
- Prompting the user; callers confirm low-confidence roots.
- Harness feature detection beyond directory markers.

## Confidence

- `high` — skills and context directories exist under the marker.
- `medium` — some expected directories exist.
- `low` — none exist, or the root fell back to VCS or home.

Callers confirm with the user before writing when confidence is `low` or a `note` is present.

## Detail

- [Interface](references/INTERFACE.md) — output schemas, marker table, resolution order, exit codes.
- [Dependencies](references/DEPENDENCIES.md)
