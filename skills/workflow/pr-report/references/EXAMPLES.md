# Examples

## Example state snippet

```markdown
## Comment History
| ID | Author | Category | First Seen | Last Status | Current Status | Confidence | Resolution | Rebuttal? |
|----|--------|----------|------------|-------------|----------------|------------|------------|-----------|
| t1-c1 | reviewer-a | human_reviewer | iter 1 | open | open | graphql | — | no |
| t2-c1 | coderabbitai | automated_reviewer | iter 1 | open | resolved | graphql | auto | no |
| t3-c1 | sonarqubecloud | static_analysis | iter 1 | open | open | graphql | — | no |
| t4-c1 | T876 | hybrid_reviewer | iter 2 | open | open | graphql | — | yes |
```

## Example issues board

```markdown
## Issues Requiring Action

| ID | Source | Severity | Category | Confidence | Why Address | Related Comments |
|----|--------|----------|----------|------------|-------------|------------------|
| I-1 | SonarQube | required | quality | high | Rule `typescript:SUnusedVariable` violated. | t3-c1 |
| I-2 | reviewer-a | required_to_resolve | bug | high | Missing validation on login form. | t1-c1 |
| I-3 | T876 (hybrid) | required_to_resolve | opinion | medium | Suggests different error message. Rebutted after our first response. | t4-c1 |
| I-4 | GitHub Actions | blocker | ci | high | Required check "Run tests" failing. 3 tests failed. | check-123 |
```

## Example chat summary

```
**PR #1234 — Iteration 3**
- **Open items needing action:** 4
- **Top issues to address:**
  - **[blocker]** GitHub Actions — 3 tests failing in AuthService.
  - **[required]** SonarQube — Remove unused import in src/auth/login.ts.
  - **[required_to_resolve]** @reviewer-a — Missing validation on login form.
  - **[required_to_resolve]** T876 (hybrid) — Rebuttal on error message wording.
- **Resolved since last check:** 2
- **Review state:** CHANGES_REQUESTED by @reviewer-a
- **CI / build status:** failing
- **Suggested next step:** fix CI, then address open SonarQube and reviewer items
- **Static analysis:** 1 finding (unchanged)
- **Unclear status:** 0 items
- **Rebuttals:** 1

Full report: `.agents/context/pr-report/OC-1234-report.md`
```
