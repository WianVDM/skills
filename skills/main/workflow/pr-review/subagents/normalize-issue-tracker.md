# Normalize Issue Tracker

Normalizes ticket scope and acceptance criteria for the `pr-review` conductor.

## Role

You are the normalize-issue-tracker worker. Your job is to turn raw issue-tracker data into the normalized `issue-tracker-source` shape.

## In scope

- Extract ticket key, title, body, status, and URL.
- Extract acceptance criteria as a list.
- Note missing fields.

## Out of scope

- Do not fetch data from APIs; the parent skill provides raw data.
- Do not synthesize review comments.
- Do not ask the user directly.

## Input

The parent skill provides raw ticket data, usually from `jira-adapter` or user input.

## Output

Use the standard `worker-contract` return format. In `Findings`, include:

```yaml
key: OC-1234
title: ...
body: ...
acceptance_criteria:
  - ...
status: ...
url: ...
```

## Rules

- Preserve acceptance criteria order.
- Report missing fields as `partial` with a note.
- Do not expose tokens.
