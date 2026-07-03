# Debrief Examples

## Example 1: bug debrief with Green confidence

### Input

- Ticket: `OC-4644`
- Tracker: Jira
- Branch: `SHB-362`

### Generated report frontmatter

```yaml
---
skill: debrief
version: 4.0
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-07-03T08:42:00Z
updated_at: 2026-07-03T08:42:00Z
summary: "Auth guard race condition during token refresh."
task_type: code
status: In Progress
priority: High
debrief_status: complete
debrief_confidence: Green (90%)
confidence_gap: []
baseline_status: complete
consumed_context:
  - {context_dir}/baseline/OC-4644-SHB-362.md
artifacts_dir: OC-4644
assumptions:
  - assumption: "Token refresh happens in auth.guard.ts."
    basis: "Code in auth.guard.ts contains refresh logic; no interceptor found."
    confidence: 85
    alignment: Reasonable inference
    disproof_signals: "ADR mentioning interceptor, code in interceptor, tests referencing refresh.interceptor."
    impact_if_wrong: "Fix would move to interceptor."
    status: resolved
---
```

### Chat summary

> "OC-4644 describes a race condition where navigating to `/dashboard` during token refresh redirects the user back to `/login`. Based on the ticket, comments, and code in `auth.guard.ts`, the guard reads `isAuthenticated()` before the refresh observable completes. I believe the fix should make the guard wait for refresh to complete before evaluating access. Baseline confirms the bug is reproducible. Confidence is Green."

---

## Example 2: vague ticket with Yellow confidence

### Chat summary

> "This ticket asks for 'better error handling' in the checkout flow but doesn't define what 'better' means. Based on the current code in `checkout.service.ts` and the pattern used in `billing.service.ts`, I believe the intent is to add user-facing error messages for failed payments and retry logic for network errors. My confidence is Yellow (75%) because the ticket lacks acceptance criteria. If you can confirm whether retry logic is in scope, I can raise confidence to Green."

---

## Example 3: Red confidence with escalation

### Chat summary

> "I cannot confidently interpret this ticket yet. The description says users should be able to delete their account, but a comment from the product owner says deletion should only be allowed by admins. The codebase currently has no admin check for account deletion. My best assumption is that the comment reflects the latest intent, but this contradicts the description. I need clarification on whether account deletion is user-initiated or admin-only before proceeding."

---

## Example 4: config after first run

```yaml
# {marker_dir}/config/debrief.yaml

preferences:
  confidence_threshold: 85
  baseline_mode: optional
  issue_tracker: jira
  project_key: OC
  max_parallel_subagents: 3
  max_related_depth: 3
  max_investigation_rounds: 5
  max_code_search_minutes: 5
  artifact_freshness_hours: 24
  auto_resolve_ambiguities: true
  monorepo_workspace: auto

  trackers:
    jira:
      server_url: https://your-domain.atlassian.net
      username: your-email@example.com
      token_env: JIRA_API_TOKEN
      username_env: JIRA_USERNAME
      mcp_server_name: jira

notes:
  - text: "Jira is the verified issue tracker for this project."
    category: decision
  - text: "Project key 'OC' detected from branch names."
    category: decision
  - text: "Tickets in this project often lack acceptance criteria; rely on related tickets and codebase patterns."
    category: gotcha
```

---

## Example 5: state file snippet

```markdown
## Context Graph
| Source | Key | Relevance | Contribution | Timestamp |
|--------|-----|-----------|--------------|-----------|
| Core ticket | OC-4644 | High | Auth guard race condition | 2026-06-26T08:00:00Z |
| Parent ticket | OC-4000 | Medium | Auth system improvements | 2026-06-26T08:05:00Z |
| Related PR | #123 | Medium | Recent auth refactor | 2026-06-26T08:10:00Z |
| Codebase | auth.guard.ts | High | Confirms role-based flow | 2026-06-26T08:15:00Z |
| Baseline | OC-4644 | High | Bug reproducible | 2026-06-26T08:42:00Z |

## Ambiguities
| Ambiguity | Status | Confidence | Resolution | Basis | Iteration |
|-----------|--------|------------|------------|-------|-----------|
| Which guard handles this? | resolved | High (85%) | auth.guard.ts | Ticket + code | 1 |
| Refresh location | resolved | Medium (70%) | Stay in guard | Code pattern | 1 |
```

---

## Example 6: blocker report

Saved when confidence is below `confidence_threshold`.

```yaml
---
skill: debrief
type: blocker-report
version: 4.0
ticket: OC-4644
branch: SHB-362
commit: abc1234
generated_at: 2026-07-03T08:42:00Z
updated_at: 2026-07-03T08:42:00Z
summary: "Ticket is too vague to proceed with confidence."
---

## What is known
- The ticket title mentions "auth guard race condition" but the description is one sentence.
- No acceptance criteria are provided.
- No related tickets or recent comments clarify the expected behavior.

## What was investigated
- Searched `auth.guard.ts`, `auth.service.ts`, and related tests for refresh logic.
- Checked for related tickets and ADRs mentioning "refresh" or "race condition".
- Attempted to contact the issue tracker; ticket comments are empty.

## What is missing
- Expected behavior after token refresh completes.
- Whether the guard should wait, retry, or redirect during refresh.
- Acceptance criteria or a reproduction scenario.

## Why the risk is too high
Any implementation choice would be a guess that changes user-facing auth behavior. The cost of getting it wrong is high and the evidence is low.

## What the user needs to clarify
1. What should happen when a user navigates to a guarded route during token refresh?
2. Should the guard block, redirect, or retry?
3. Is there a reproduction scenario or design note available?
```
