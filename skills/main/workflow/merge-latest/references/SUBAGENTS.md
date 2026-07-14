# Subagent Delegation

`merge-latest` delegates focused tasks to workers. The main skill orchestrates and integrates results.

## Standard worker return format

Workers should return structured markdown:

```markdown
---
status: complete
---

## Summary
Brief summary.

## Findings
Structured findings.

## Recommended Next Action
What the main agent should do next.
```

Status values: `complete`, `in-progress`, `blocked`.

## Subagents

| Subagent | Responsibility |
|----------|----------------|
| `latest-fetcher` | Fetch remote refs and fast-forward the local target branch when safe. |
| `branch-researcher` | Investigate branch relationships and infer the upstream branch with high confidence. |
| `preflight-checker` | Run pre-flight validation checks, including checkout and stash handling. |
| `recon-runner` | Run reconnaissance and gather merge metadata using resolved remote refs. |
| `conflict-classifier` | Classify each conflict as trivial, semantic, or review. |
| `conflict-investigator` | Deep analysis of complex conflicts; produces per-file briefs and safe recommendations. |
| `validation-runner` | Run the user-configured validation command pipeline. |
| `report-writer` | Compile the merge report and chat summary. |
| `checkpoint-manager` | Track state, phase checklist, and resume state. |

Workers do not modify the working tree unless explicitly instructed. They return findings and recommendations.
