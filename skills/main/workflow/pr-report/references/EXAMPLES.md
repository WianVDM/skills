# Examples

## Full sweep: chat summary

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

Full report: `.agents/context/pr-report/OC-1234-report.md`
```

## Focused mode

- `/pr-report ci` — collect only CI / build status.
- `/pr-report reviews` — collect only top-level, inline, and conversation feedback.
- `/pr-report static-analysis` — collect only static-analysis findings.

In focused mode, the report contains only the requested section, plus the **Data sources** section and a short summary.

## Degraded-source disclosure

When a degraded source is used with `degraded_mode: ask`:

> The SonarQube MCP returned no issues for this branch, which is inconclusive for PR analyses. I used the SonarCloud API with `pullRequest=1234` instead and found 4 findings. If you want me to try a different source, confirm and I will rerun that section.

And the corresponding **Data sources** entry:

> `static_analysis`: SonarCloud API (`pullRequest` query). SonarQube MCP was preferred but inconclusive for PR analyses; fallback taken automatically per ranking. Confidence: high.
