# HTML Renderer

Follow the `worker-contract` return contract. Renders the optional human-facing HTML dashboard from the canonical Markdown report.

## In scope

- Convert the Markdown PR report into a readable HTML file.
- Include summary cards and an issue board with severity and source filters.
- Link back to the canonical Markdown report.

## Out of scope

- Altering the Markdown report.
- Writing to the state file.

## Inputs

- Path to the Markdown report
- Desired output path for the HTML file

## Outputs

Return the standard worker contract with the HTML artifact path and a summary of rendered sections.

## Rules

- The Markdown report remains canonical; HTML is a human-friendly view.
- Include summary cards for open issues, resolved items, CI status, and review state.
- The HTML dashboard includes severity and source filters for the issue board.
- Link back to the canonical Markdown report.
- Escalate to `needs_input` if the Markdown report is missing or unreadable.
