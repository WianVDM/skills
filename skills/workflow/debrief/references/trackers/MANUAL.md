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

> "I couldn't find a connected issue tracker. To debrief this ticket, please help me understand it by providing:
> - Ticket key or identifier
> - Title or summary
> - Description
> - Acceptance criteria or expected behavior
> - Any related context, screenshots, links, or files
> You can paste the details here or point me to a Markdown file."

## State handling

Store the user-provided context in `## Ticket Context Cached` in the state file. Treat it as the primary source for the debrief.

## Limitations

- No automated related-ticket discovery.
- No attachment downloads.
- No development info from tracker.
- Heavier reliance on codebase exploration and user input.

## When to prefer manual

Manual input can also supplement an automated tracker. If the user says "also consider this context," add it to the context graph regardless of the tracker.
