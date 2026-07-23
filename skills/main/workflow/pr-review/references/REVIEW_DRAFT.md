# Review draft format

The PR-facing artifact: exactly what gets posted to the pull request, and nothing else. Written by `review-writer` from the user's approved findings.

**What never appears in this file:** confidence statements, posting-readiness notes, process narration ("I checked X", "skipped Y"), scope-drift discussion, settled-item discussion, open questions for the user. Those belong to the user-facing report (`REVIEW_REPORT.md`). If a sentence is addressed to the person who ran the skill rather than the PR's author, it is in the wrong file.

## File location

`{context_dir}/pr-review/{key}/{key}-review-draft.md`

## Frontmatter

```yaml
---
event: APPROVE
repo: owner/repo
pr_number: 42
commit_id: abc123def456
status: draft
---
```

| Field | Description |
|---|---|
| `event` | `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`. Chosen per the rubric's event rules. |
| `repo` | `owner/repo`. |
| `pr_number` | Pull request number. |
| `commit_id` | HEAD commit SHA at review time. |
| `status` | `draft` until the user confirms, then `confirmed`. |

## Body

The top-level comment. A few sentences, not a report.

- **Approvals.** Start with the configured opener (`review.style.approve_opener`, default `"Looks good to me.."`). Anything after the opener is short: context the author needs, or a pointer to the inline comments. No summary of what the reviewer did.
- **Request changes.** One or two sentences: what must change and why. The detail lives in the inline comments, not here.
- **Comment.** One or two sentences stating the reviewer's position and what they are waiting on.

The body never narrates process, never lists what was checked, never hedges. If there is nothing worth saying beyond the opener, the body is the opener.

## Inline comments

```yaml
- path: src/auth/login.ts
  line: 42
  side: RIGHT
  label: issue
  decorations: [blocking]
  body: |
    Empty passwords reach the hash call and throw.
    Validate here or return a 400 before this point.
```

| Field | Description |
|---|---|
| `path` | File path relative to repo root. |
| `line` | Line number inside a changed diff hunk. |
| `side` | `RIGHT` (new version) by default; `LEFT` for the old version. |
| `label` | One of the rubric's labels: `issue`, `suggestion`, `question`, `nitpick`, `praise`, `note`, `todo`, `chore`. |
| `decorations` | `blocking`, `non-blocking`, or `if-minor`. Default: `issue` is blocking; everything else is non-blocking. |
| `body` | One to three sentences. Behavior-first. The label prefix is rendered into the posted text only when `review.style.render_labels` is on. |

## Anchoring rules

- Anchor every comment to a line inside a changed diff hunk.
- A finding about unchanged code anchors to the nearest changed line and names the real target in the text ("two methods up, `validate()` also...").
- Never post a line number outside the PR diff.

## Voice rules

- Human voice, maintainer tone. Short and direct.
- No hedge phrases ("it is important to note"), no vague intensifiers ("robust", "crucial"), no abstract verbs ("leverage", "navigate"), no meta-narration ("this review aims to").
- Question-first unless the finding is a confirmed defect (see the rubric).
- No placeholder text — no "TODO", no "test", no templates left unfilled.
- The signal-to-noise budget applies at write time: if a comment does not change what the author does next, cut it.
