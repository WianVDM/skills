# Issue Synthesizer

A focused worker for the `pr-report` skill. Groups, challenges, and weights feedback to produce a concise issue board.

## In scope

- Turn raw comments and findings into actionable, deduplicated issues.
- Identify resolved items, rebuttals, and dismissed feedback.
- Suggest the next step based on the synthesized board.

## Out of scope

- Do not fetch new PR data here.
- Do not write to report or state files.

## Inputs

The parent skill provides:

- PR metadata
- Normalized review threads
- Static-analysis findings
- CI failures
- Scope flags
- Bot/source mappings from config
- Ticket scope / acceptance criteria

## Outputs

Use the standard worker return contract.

```yaml
---
status: complete | partial | needs_input | blocked
artifacts: []
---
```

## Summary
Overall issue health and the top concerns requiring attention.

## Findings

### Issues Requiring Action
| ID | Source | Severity | Category | Confidence | Why Address | Related Comments / Findings |
|----|--------|----------|----------|------------|-------------|------------------------------|

### Resolved Since Last Check
| Item | Source | How | Notes |
|------|--------|-----|-------|

### Addressed by Us — Pending Resolve
| Item | Source | Our Response |
|------|--------|--------------|

### Rebuttals Requiring Response
| Item | Reviewer | Their Reply |
|------|----------|-------------|

### Dismissed / No Action Needed
| Item | Source | Reason |
|------|--------|--------|

### Top Issues for Chat Summary
| Severity | Source | One-line Summary |
|----------|--------|------------------|

## Decisions made
- Severity downgraded because a comment did not survive challenge against scope or changes.
- Duplicate concerns grouped under a single issue.

## Open questions
- ...

## Blockers
- Missing ticket scope prevents confident challenge.

## Rules

- Challenge every comment against ticket scope and actual PR changes.
- Group duplicate or near-duplicate concerns across reviewers and bots.
- Apply source-type severity defaults from config.
- Downgrade severity when a comment does not survive challenge.
- Never report an uncertain thread as open.
- Suggested next step: address open items, re-request review, wait for reviewer, or fix CI.
- Do not ask the user directly unless explicitly authorized. If you need user input, return `status: needs_input` with the exact question and options.
