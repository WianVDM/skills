# Examples

## Example state snippet

```markdown
## Comment History
| ID | Author | Category | First Seen | Last Status | Current Status | Confidence | Resolution | Rebuttal? |
|----|--------|----------|------------|-------------|----------------|------------|------------|-----------|
| t1-c1 | reviewer-a | human_reviewer | iter 1 | open | open | high | — | no |
| t2-c1 | coderabbitai | automated_reviewer | iter 1 | open | resolved | high | auto | no |
| t3-c1 | sonarqubecloud | static_analysis | iter 1 | open | open | high | — | no |
| t4-c1 | T876 | hybrid_reviewer | iter 2 | open | open | medium | — | yes |
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

## Example task list

```markdown
## Task List

- Fix failing tests in `src/auth/login.test.ts`.
- Reply to @reviewer-a about form validation on the login form.
- Dismiss SonarCloud unused-import warning in `src/auth/login.ts` if it is intentional.
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

## Example manual fallback input

When no PR tool is configured, the conductor asks for the data directly. A valid Markdown input with frontmatter looks like:

```markdown
---
pr_number: 1234
repo: owner/repo
branch: feature/OC-1234-login-validation
base: origin/main
state: open
---

# PR: Add validation to login form

## Changed files

- src/auth/login.ts
- src/auth/login.test.ts
- src/components/LoginForm.tsx

## Open comments

- @reviewer-a: Missing validation on the password field.
- @coderabbitai: Consider extracting the validation logic into a helper.

## CI status

- Run tests: failing (3 failures in src/auth/login.test.ts)
```

The conductor normalizes this into the internal model and proceeds to triage.

## Example focused mode invocation

- `/pr-report ci` — collect only CI / build status.
- `/pr-report reviews` — collect only top-level and inline review feedback.
- `/pr-report static-analysis` — collect only static-analysis findings.

In focused mode, the report contains only the requested section, plus the **Data sources** section and a short summary.
