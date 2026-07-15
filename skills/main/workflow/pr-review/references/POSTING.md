# Posting gate

Confidence rules and manual fallback for posting a PR review.

## Confidence levels

| Level | Conditions | Action |
|---|---|---|
| `high` | Tool is configured and tested; line coordinates verified against diff hunks; user explicitly approved. | Post in one shot. |
| `medium` | Some uncertainty about tool behavior or line coordinates. | Do not post; provide manual payload. |
| `low` | Missing data, untested tool, or conflicting information. | Do not post; provide manual payload and explain gaps. |

## Posting checklist

Before posting, confirm all of the following:

1. The user has explicitly approved the exact draft.
2. Every inline comment line is inside a changed diff hunk.
3. The `commit_id` matches the current PR head.
4. The posting tool is available and has required permissions.
5. The payload is complete: `event`, `body`, `commit_id`, `comments`.

## Posting flow

1. Assemble the payload from the confirmed draft.
2. Validate coordinates by mapping each comment to the diff hunk.
3. Invoke the preferred posting tool with the full payload.
4. If the post succeeds, record the URL and set state to `complete`.
5. If the post fails with a 422 or line-resolution error:
   - Fix the coordinate if the cause is clear and retry confidence remains high.
   - Otherwise, stop and hand back the manual payload.

## Manual fallback

Write the exact payload to `{context_dir}/pr-review/{key}/{key}-review-payload.md`:

```yaml
---
event: REQUEST_CHANGES
repo: owner/repo
pr_number: 42
commit_id: abc123def456
---

## Body
...

## Comments
- path: src/auth/login.ts
  line: 42
  side: RIGHT
  body: ...
```

Tell the user how to post it manually (e.g., via GitHub UI or `gh pr review`).

## Never allowed

- Posting without explicit user confirmation.
- Posting placeholder or "test" reviews.
- Leaving a partial review on the PR.
- Posting when confidence is medium or low.
