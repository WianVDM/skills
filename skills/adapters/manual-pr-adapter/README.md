# manual-pr-adapter

Manual PR source adapter for `pr-report`.

## Purpose

Collect PR metadata, changed files, and review feedback from user input, CSV, JSON, or markdown files. This is the fallback adapter for unsupported tools or manual processes.

## When to use

- No API-based PR provider is available.
- The user has PR data in a spreadsheet, document, or chat export.

## Inputs

Mode (`interactive`, `csv`, `json`, `markdown`, or `mixed`) plus optional file paths or repo identifier.

## Outputs

Normalized PR data in the standard `pr-source` adapter shape.

## Supported formats

- Interactive paste
- CSV
- JSON
- Markdown
