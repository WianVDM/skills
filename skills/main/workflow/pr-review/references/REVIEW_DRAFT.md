# Review draft format

Format and style rules for the review draft written by `pr-review`.

## File location

`{context_dir}/pr-review/{key}/{key}-review-draft.md`

## Frontmatter

```yaml
---
event: REQUEST_CHANGES
repo: owner/repo
pr_number: 42
commit_id: abc123def456
confidence: high
status: draft
---
```

| Field | Description |
|---|---|
| `event` | `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`. |
| `repo` | Repository in `owner/repo` format. |
| `pr_number` | Pull request number. |
| `commit_id` | HEAD commit SHA at review time. |
| `confidence` | Overall confidence (`high`, `medium`, `low`). |
| `status` | `draft` until confirmed, then `confirmed`. |

## Body

The top-level review body contains:

- A concise summary of the PR's purpose and intent.
- A clear verdict: approve, comment, or request changes.
- A list of required and optional items.
- A confidence statement.
- A note about whether the draft is ready to post.

## Inline comments

Each inline comment has:

```yaml
- path: src/auth/login.ts
  line: 42
  side: RIGHT
  body: |
    Add validation for the case where the password is empty.
    severity: required
    confidence: high
```

| Field | Description |
|---|---|
| `path` | File path relative to repo root. |
| `line` | Line number in the diff. |
| `side` | `RIGHT` for the new version, `LEFT` for the old version. Default `RIGHT`. |
| `body` | Comment text. |
| `severity` | `required` or `optional`. |
| `confidence` | `high`, `medium`, or `low`. |

## Anchoring rules

- Anchor comments to lines inside changed diff hunks.
- If a comment must reference unchanged code, anchor it to the nearest changed line and mention the target line in the comment text.
- Do not use line numbers that are outside the PR diff.

## Style rules

- Be specific. Cite behavior, not just style.
- Distinguish required changes from suggestions.
- Avoid repeating comments already present on the PR.
- Reference ticket acceptance criteria when relevant.
- Keep the top-level body concise; put detailed feedback in inline comments.
- Never include placeholder text such as "TODO" or "test".
