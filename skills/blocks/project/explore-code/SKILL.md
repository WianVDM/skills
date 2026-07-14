---
name: explore-code
description: "Search the codebase for evidence related to a specific question, ticket, or ambiguity. Find mentioned files, similar patterns, relevant tests, ADRs, and docs. Use when a skill needs code context to resolve uncertainty."
version: 1.0.0
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [codebase, exploration, evidence, building-block]
allowed-tools:
  - bash
---

# explore-code

## Identity

`explore-code` is a deterministic building-block skill that searches a codebase for evidence related to a ticket, question, or ambiguity. It answers: *"What does the codebase say about this?"*

## Purpose and type

- **Type**: Building-block skill / deterministic script wrapper.
- **Purpose**: Bridge a ticket or question to the codebase by finding mentioned files, comparable patterns, and relevant source/tests/ADRs, then return ranked evidence.
- **Judgment**: Low. The script uses deterministic heuristics to rank files; the caller (usually a conductor) interprets the evidence.

## In scope

- Find files explicitly mentioned in a ticket or caller input.
- Search for similar patterns or comparable features using keywords extracted from the ticket summary or question.
- Read relevant source files, tests, ADRs, and docs to confirm existence and capture a content summary.
- Score files by relevance using deterministic heuristics: direct mention, keyword overlap, path hints (e.g., `test/`, `docs/`, `adr/`), and file type.
- Respect workspace scoping for monorepos when `workspace` is provided.
- Apply a time-box target (`time_box_minutes`) and a hard file-count limit (`max_files`, default 20).
- Compare ticket claims against code evidence and report contradictions or confirmations.
- Return a structured JSON envelope with status, relevant files, snippets, and gaps.

## Out of scope

- Do not form assumptions about intent or recommend implementations.
- Do not write, edit, or delete code, tests, or docs.
- Do not perform broad architecture reviews outside the scope of the provided question/ticket.
- Do not ask the user questions directly; return `status: needs_input` only when required inputs are missing.
- Do not replace downstream analysis (e.g., confidence calculation, planning) — only gather evidence.

## When to use

- A conductor such as `debrief` needs to resolve a code-related ambiguity.
- A skill needs to know how a ticket or feature maps to the codebase.
- A user asks: *"Where does X happen in the code?"* or *"What files relate to this ticket?"*

## Input / output contract

### Input

The skill accepts a JSON object via stdin to `scripts/explore-code.py`.

```json
{
  "ticket_summary": "Auth guard race condition during token refresh",
  "mentioned_files": ["src/app/guards/auth.guard.ts"],
  "task_type": "code",
  "workspace": null,
  "project_root": null,
  "force": false,
  "time_box_minutes": 5,
  "max_files": 20
}
```

| Field | Required | Default | Description |
|---|---|---|---|
| `ticket_summary` | yes | — | Ticket summary, question, or short description to search against. |
| `mentioned_files` | no | `[]` | Files explicitly mentioned in the ticket. Paths can be relative or absolute. |
| `task_type` | no | `"code"` | One of `code`, `ui`, `docs`, `process`. Exploration is skipped for `process` unless `force` is true. |
| `workspace` | no | `null` | Monorepo workspace name to scope searches. Resolved relative to `project_root` (or the current working directory if no project root is supplied). |
| `project_root` | no | `null` | Project root directory used to resolve `workspace` and relative paths. Defaults to the current working directory. |
| `force` | no | `false` | When true, run exploration even for `process` task types. |
| `time_box_minutes` | no | `5` | Target time budget in minutes; used to limit search breadth. |
| `max_files` | no | `20` | Maximum number of relevant files to return. |
| `min_relevance` | no | `"Low"` | Minimum relevance threshold to include in results. One of `High`, `Medium`, `Low`. |
| `read_limit_lines` | no | `200` | Maximum number of lines to read from a discovered file when generating a `content_summary`. |

### Output

```json
{
  "status": "complete",
  "relevant_files": [
    {
      "path": "src/app/guards/auth.guard.ts",
      "relevance": "High",
      "reason": "explicitly mentioned in ticket"
    }
  ],
  "snippets": [
    {
      "path": "src/app/guards/auth.guard.ts",
      "content_summary": "canActivate checks isAuthenticated before refresh completes"
    }
  ],
  "missing_files": []
}
```

| Field | Description |
|---|---|
| `status` | `complete`, `partial`, `blocked`, or `needs_input`. |
| `relevant_files` | Ranked list of `{path, relevance, reason}`. |
| `snippets` | Summarized content for the top files. |
| `missing_files` | Mentioned files that could not be found. |

### Status values

| Status | Meaning | Caller action |
|---|---|---|
| `complete` | Search completed within time and file limits. | Use evidence. |
| `partial` | Some files searched or limits hit; results are incomplete. | Note gaps. |
| `blocked` | Tool or filesystem error prevented searching. | Investigate. |
| `needs_input` | Required input missing (e.g., empty `ticket_summary`). | Surface to user. |

## Lazy loading

`explore-code` is only invoked when the task type is `code` or `ui`, or when a specific ambiguity is code-related. It does not run for pure `process` tickets. The script itself is stateless and performs no eager initialization.

## Dependencies

See `references/DEPENDENCIES.md` for required tools, binaries, and skills.

See `references/CONFIG_PATTERN.md` for supported configuration keys.

## Example usage by a conductor

```text
Run explore-code with ticket_summary "Auth guard race condition during token refresh", mentioned_files ["src/app/guards/auth.guard.ts"], task_type "code", max_files 20.
```

```text
Run explore-code with question "Where is token refresh handled?", workspace "frontend", time_box_minutes 3.
```

## Implementation notes

- The deterministic entry point is `scripts/explore-code.py`.
- The script uses `ripgrep` (`rg`) when available, and falls back to Python's built-in directory walk. It does not call LLMs.
- `workspace` is resolved relative to `project_root` (or the current working directory) to keep monorepo scoping safe.
- Relevance is scored heuristically; callers should treat rankings as evidence, not decisions.
- No LLM calls are made inside the script.

## Security and safety

- Read-only: the script does not modify the codebase.
- Respects the provided `workspace` path scope; does not escape outside the workspace or project root.
- Does not execute code from discovered files.
- No secrets are read or transmitted.
