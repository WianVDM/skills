# HTML Renderer

A focused worker for the `pr-report` skill. Renders the optional human-facing HTML dashboard from the canonical Markdown report.

## In scope

- Convert the Markdown PR report into a readable HTML file.
- Include summary cards and a filterable issue board when supported.
- Link back to the canonical Markdown report.

## Out of scope

- Do not alter the Markdown report.
- Do not write to the state file.

## Inputs

The parent skill provides:

- Path to the Markdown report
- Desired output path for the HTML file

## Outputs

Use the standard worker return contract.

```yaml
---
status: complete | partial | needs_input | blocked
artifacts:
  - {html-output-path}
---
```

## Summary
Whether the HTML dashboard was generated and where it is located.

## Findings

### HTML Output
{path}

### Sections Rendered
- Summary cards
- Issue board
- CI status panel
- Reviewer status
- Scope flags

## Decisions made
- ...

## Open questions
- ...

## Blockers
- Markdown report missing or unreadable.

## Rules

- The Markdown report remains canonical; HTML is a human-friendly view.
- Include summary cards for open issues, resolved items, CI status, and review state.
- Make the issue board filterable by severity and source if the output format supports it.
- Link back to the canonical Markdown report.
- Do not ask the user directly unless explicitly authorized. If you need user input, return `status: needs_input` with the exact question and options.
