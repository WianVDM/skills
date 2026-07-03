# Assumption Handling

Vague tickets require assumptions. The `debrief` skill forms assumptions explicitly, challenges them, and only escalates when confidence is low or contradictions exist.

---

## When to form an assumption

Form an assumption when:

- The ticket is unclear about intent.
- Multiple interpretations are possible.
- Codebase evidence points toward one interpretation.
- Related tickets or comments suggest a pattern.

Do not form an assumption when:

- The ticket explicitly states the requirement.
- The user has already clarified.
- No evidence supports any interpretation.

---

## Assumption format

Every assumption should include:

```markdown
### {what was unclear}
- **Assumption:** {what you believe is most likely intended}
- **Basis:** {ticket context + code evidence that supports this}
- **Confidence:** {High | Medium | Low} ({0-100}%)
- **Alignment:** {Fully aligned | Reasonable inference | Potentially divergent}
- **What would disprove it:** {specific evidence that would invalidate the assumption}
- **Impact if wrong:** {how implementation would change}
```

---

## Confidence and alignment

| Confidence | Range | Action |
|------------|-------|--------|
| **High** | ≥80% | Document as resolved. Do not escalate. |
| **Medium** | 50-79% | Document as resolved. Note the risk. Proceed unless it affects core behavior. |
| **Low** | <50% | Document as requiring clarification. Escalate to user. |

**Alignment assessment:**

- **Fully aligned** — assumption clearly fits ticket scope and existing patterns.
- **Reasonable inference** — assumption is logical but not explicitly confirmed.
- **Potentially divergent** — assumption may depart from ticket intent. Treat as Medium at best; escalate if it affects acceptance criteria.

---

## Challenge process

For each assumption, the `assumption-challenger` subagent performs a disproof search:

1. **Restate the assumption** in falsifiable form.
2. **Identify disproof signals** — what evidence would prove this wrong?
3. **Search for those signals** in:
   - Ticket comments and related tickets.
   - ADRs and documentation.
   - Codebase patterns and recent changes.
   - Open PRs and commits.
   - Tests and test names.
4. **Report findings** — evidence found, evidence absent, or inconclusive.

### Example

Assumption: "Token refresh happens in `auth.guard.ts`."

Disproof signals:

- An ADR or comment says refresh was moved to an interceptor.
- Code exists in an interceptor that handles refresh.
- Tests reference `refresh.interceptor.ts` or similar.
- A linked PR removes refresh logic from the guard.

If any signal is found, revise or escalate.

---

## Hard escalation rules

Always escalate to the user (do not assume) when:

- The ticket explicitly states X and you believe Y is better.
- The ambiguity concerns a fundamental behavioral change and you have zero code evidence.
- The ambiguity affects acceptance criteria and your confidence is Low.
- The ticket contradicts itself, related tickets, or the codebase.

---

## Communicating uncertainty

When escalating, use natural language. Never leave a bare question.

### Bad

> "Where should token refresh happen?"

### Good

> "The ticket describes the symptom but not where the fix should live. Based on `auth.guard.ts` and the related ticket OC-1234, I believe the refresh should stay in the guard. If your team has discussed moving refresh to an interceptor, the fix would change significantly. Can you confirm which approach is preferred?"

Every escalation should include:

1. **Your best assumption.**
2. **Why you believe it.**
3. **What would change your mind.**
4. **The specific information you need.**
