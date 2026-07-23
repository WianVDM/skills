# Posting gate

Confidence rules and the manual fallback for posting a PR review. This file owns the posting-gate rules; SKILL.md carries only a two-line summary and links here.

## Confidence levels

| Level | Conditions | Action |
|---|---|---|
| `high` | User approved the exact draft; every coordinate validated by `scripts/validate-review-coordinates.py`; `commit_id` matches the PR head; posting tool present and authenticated. | Post in one shot. |
| `medium` | Some uncertainty about tool behavior, auth, or coordinates. | Do not post; provide the manual payload. |
| `low` | Missing data, untested tool, or conflicting information. | Do not post; provide the manual payload and explain gaps. |

Always ask for explicit approval before posting, even at high confidence.

## Posting flow

1. Assemble the complete payload from the confirmed draft: `event`, `body`, `commit_id`, `comments`.
2. Validate coordinates by running `scripts/validate-review-coordinates.py` with the diff and all comments. Any invalid coordinate sends the draft back to the user — never fix silently.
3. Post via the selected posting tool **in one call**. On GitHub, follow the `post-github-pr-review` skill: one `github_create_pull_request_review` call with the complete payload; never body-first, never split comments out of the review.
4. If the post succeeds, record the URL and set state to `complete`.
5. If the post fails with a 422 or line-resolution error, fix the coordinate only when the cause is unambiguous and the user confirms; otherwise hand back the manual payload.

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
  body: |
    issue (blocking): Empty passwords reach the hash call and throw.
    Validate here or return a 400 before this point.
```

Tell the user how to post it manually (platform web UI, or `gh pr review` / `glab mr note` equivalents). The payload must be complete enough to paste without editing.

## Never allowed

- Posting without explicit user confirmation.
- Posting placeholder or "test" reviews.
- Leaving a partial review on the PR (body posted without its comments).
- Posting when confidence is medium or low.
- Posting any content from the user-facing report. Only the confirmed PR-facing draft is postable.
