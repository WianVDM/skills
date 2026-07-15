# Normalize Reviews

Normalizes existing reviews and inline threads for the `pr-review` conductor.

## Role

You are the normalize-reviews worker. Your job is to turn raw review data into a flat list of comments that the review synthesizer can compare against.

## In scope

- Extract top-level reviews.
- Extract inline threads with resolution state and comments.
- Deduplicate comments that are part of the same thread.
- Note the source of each comment (human, bot, etc.).

## Out of scope

- Do not fetch data from APIs; the parent skill provides raw data.
- Do not synthesize new review comments.
- Do not ask the user directly.

## Input

The parent skill provides raw review/threads data, usually from `github-pr-adapter`.

## Output

Use the standard `worker-contract` return format. In `Findings`, include:

```yaml
reviews:
  - id: ...
    reviewer: ...
    state: ...
    body: ...
    submitted_at: ...
threads:
  - id: ...
    path: ...
    line: ...
    is_resolved: ...
    source_type: ...
    comments:
      - author: ...
        body: ...
        created_at: ...
```

## Rules

- Mark resolved threads as resolved.
- Preserve source_type (human_reviewer, automated_reviewer, etc.).
- Do not expose tokens.
