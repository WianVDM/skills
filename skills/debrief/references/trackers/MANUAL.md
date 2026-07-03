# Manual Tracker Adapter

Fallback adapter when no issue tracker is configured or available.

## When to use

- No issue tracker MCP server is configured.
- The user declines to set one up.
- The ticket context lives outside any tracker (e.g., in a document or conversation).

## Input sources

The user can provide context via:

- Direct message in chat.
- A file path to a markdown document.
- A pasted description.

## Prompt

> "No issue tracker is configured. Please provide the ticket details:
> - Ticket key or identifier
> - Title/summary
> - Description
> - Acceptance criteria or expected behavior
> - Any relevant context, screenshots, or related information"

## State handling

Store the user-provided context in `## Ticket Context Cached` in the state file. Treat it as the primary source for the debrief.

## Limitations

- No automated related-ticket discovery.
- No attachment downloads.
- No development info from tracker.
- Heavier reliance on codebase exploration and user input.

## When to prefer manual

Manual input can also supplement an automated tracker. If the user says "also consider this context," add it to the context graph regardless of the tracker.
