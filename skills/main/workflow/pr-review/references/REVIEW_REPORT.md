# Review report format

The user-facing artifact: everything the skill knows, addressed to the person who ran it. This is where process notes, confidence, and judgment calls live — kept out of the PR-facing draft (`REVIEW_DRAFT.md`).

Long is fine here. Direct is still required.

## File location

`{context_dir}/pr-review/{key}/{key}-review-report.md`

## Frontmatter

```yaml
---
repo: owner/repo
pr_number: 42
commit_reviewed: abc123def456
generated_at: 2026-07-20T14:32:00Z
depth: full
confidence: high
status: completed
---
```

| Field | Description |
|---|---|
| `commit_reviewed` | HEAD commit SHA the findings are based on. |
| `depth` | `full`, or `degraded` when the size gate tripped or context was missing. |
| `confidence` | Overall confidence in the findings: `high`, `medium`, `low`. |

## Sections

### Summary

What the PR does, the recommended event (`APPROVE` / `COMMENT` / `REQUEST_CHANGES`), and why, in a few sentences. State the user's reviewer position (first reviewer, or after an existing approval) and which optional-comments policy was applied.

### Findings

One entry per proposed review item, whether or not it made the draft:

```yaml
- class: functionality
  label: issue
  blocking: true
  path: src/auth/login.ts
  line: 42
  confidence: high
  finding: Empty passwords reach the hash call and throw.
  evidence: No validation on the empty case; hash() raises on empty input (line 58).
  in_draft: true
```

Items cut by the signal-to-noise budget or the reviewer-position policy appear here with `in_draft: false` and the reason.

### Settled discussion

Items the PR conversation already resolved, with evidence:

```yaml
- topic: No retry on webhook delivery
  disposition: deferred
  evidence: "Author: 'deferring retries to PROJ-456, out of scope here' (issue comment, 2026-07-18)"
  question: Re-flag or drop?
```

The skill never suppresses these silently and never re-posts them to the PR without the user's answer.

### Open discussion

Raised items with no resolution — unanswered threads, disputed points. These are candidates for the draft.

### Scope check

The `scope-checker` output: in-scope, out-of-scope, and ambiguous changes relative to ticket scope and PR intent. Scope drift is reported here, not on the PR, unless the user says otherwise.

### Checks run

Each targeted check: name, command, exit code, summary. Skipped checks with reasons.

### CI and static analysis

CI state, failing jobs, static-analysis findings — or the documented skip/degradation for each.

### Skips and degradations

Every capability that produced partial or no data, what was used instead, and whether the user consented.

### Size gate

Changed-line count, whether the gate tripped, and what that means for the depth of these findings.

### Open questions

Anything the skill needs from the user before the draft can be finalized: re-flag decisions, ambiguous scope items, degraded-source consent.

## Rules

- Addressed to the operator, never copied to the PR.
- Every finding carries evidence. No bare assertions.
- Settled items always carry the evidence quote and source.
- Written in the same human voice as everything else — plain, specific, no filler.
