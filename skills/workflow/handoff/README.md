# handoff

Write a session handoff snapshot in multiple passes, from a high-level overview to detailed context, so a fresh session can continue.

## Usage

- `handoff` — write a standard handoff for the current session.
- `handoff quick` — write a compact single-pass snapshot.
- `handoff thorough` — write a deep multi-pass snapshot.
- `handoff {key}` — write a handoff tied to a ticket key or session alias.
- `handoff {level} {key}` — combine level and key, e.g. `handoff thorough ABC-123`.

## Where the file is written

The snapshot is written as a context report under the detected project context directory:

```text
{context_dir}/handoff/{normalized-key}.md
```

Without a key, it is written to:

```text
{context_dir}/handoff/unticketed.md
```

Keys are normalized to lowercase letters, digits, and hyphens. For example, `ABC-123` becomes `abc-123`.

## Archive behavior

By default, if a handoff for the same key already exists, the old file is archived to:

```text
{context_dir}/handoff/{key}-{timestamp}-archive.md
```

The new handoff then links to the archived file in its `Chain` section. Archiving preserves history without breaking the single-file-per-key convention of the `context-reports` pattern.

## Levels

| Level | Passes | Best for |
|---|---|---|
| **quick** | 1 | Short or simple sessions. |
| **standard** | 4 | Most sessions; default. |
| **thorough** | 5 | Long, complex, or high-stakes sessions. |

### Standard / thorough pass pipeline

1. **Segment and overview** — identify major phases and summarize each.
2. **Expand** — add detail to each section.
3. **Zoom in** — expand the sections that need more context.
4. **Deep zoom** — add another layer of detail (thorough only).
5. **Anchor and readiness** — ensure the first and last sections have full context and that a fresh session could continue.

## Configuration

The first time the skill runs in a project, it initializes a config file at `.agents/config/handoff.yaml`. Config keys:

- `handoff.default_level` — default level when the user does not specify one.
- `handoff.archive_old` — whether to archive an existing handoff before writing a new one.
- `handoff.include_chain` — whether to include a link to the previous handoff.

Shared keys such as `agents.context_dir` and `agents.config_dir` live in `.agents/config/shared.yaml`.

## Dependencies

- Python 3.10 or later.
- Optional: `detect-project-context` to locate the context directory.
- Recommended: `context-reports` for the shared report conventions.

## How it works

The agent uses `scripts/handoff-helper.py` to resolve the output path, archive old handoffs, and manage configuration. The helper never overwrites or deletes existing handoff files.

## Resuming from a handoff

A new session can continue by loading the latest handoff file, or by using a context-resumption skill such as `context-reports`.
