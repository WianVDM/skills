# Context reports

## Produced reports

- `.agents/context/verify-branch/{branch-name}.md`
  - Canonical verification report for a branch.
  - Contains the gate summary, verdict, findings, and consumed context.
- `.agents/context/verify-branch/{branch-name}-state.md`
  - Resume anchor and gate checklist.
  - Used to continue a verification run after an interruption.

## Consumed reports

The skill may read any fresh report in `.agents/context/{type}/{key}.md` when the filename or frontmatter matches the current branch or ticket.

Consumed reports are advisory only. They are never used to compute the verdict.

## Report schema

### Frontmatter

```yaml
---
skill: verify-branch
version: 4
branch: feature/OC-1234
base: origin/main
commit: abc1234
generated_at: 2026-06-30T20:00:00Z
verdict: FAIL
required_gates_passed: 2
required_gates_total: 3
optional_gates_passed: 1
optional_gates_total: 2
consumed_context:
  fresh:
    - path: .agents/context/baseline/OC-1234-feature-x-main.md
      skill: baseline
      summary: "Bug reproduced on auth guard."
  stale:
    - path: .agents/context/debrief/OC-1234-auth-guard.md
      skill: debrief
      reason: "commit mismatch: report is abc1234, current is def5678"
---
```

## Freshness rules

A report is considered stale if any of the following is true:

- The `branch` field differs from the current branch.
- The `commit` field differs from the current commit.
- The `generated_at` timestamp is older than the last relevant commit on the branch.

Stale reports are noted in the `consumed_context` section but never influence the verdict.

## Cross-skill consumption guidance

- Treat reports from other skills as advisory context.
- Do not let another skill's report change a PASS to FAIL or a FAIL to PASS.
- If a report contains evidence that a gate was already run, still re-run the gate to produce a current verdict.
