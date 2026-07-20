# Dependencies

## Required skills

- `detect-project-context` — locate the project root and recommended config directory.
- `list-available-skills` — discover installed skills in the target scope.
- `initialize-skill` — per-skill config mechanics: load defaults, merge with existing project config, migrate schema, persist after approval. This skill owns only the cross-skill graph (dedupe, `${ref}` inference, question ordering).
- `context-reports` — shared conventions for the context report written during finalize. Required for the **lazy** and **full** branches; unused in **preview**, so evaluate it lazily per branch rather than in pre-flight.

## Required tools

- `read`, `write`, `edit` — core agent tools.

## Required binaries

None.

## Required environment variables

None.
