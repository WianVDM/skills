# Subagent Delegation

Orchestrate delegates focused work to subagents. Each subagent has a narrow scope and a structured return contract.

## Subagent list

| Subagent | File | Responsibility |
|----------|------|----------------|
| context-loader | `subagents/context-loader.md` | Load or bootstrap required context reports. |
| plan-runner | `subagents/plan-runner.md` | Run `plan-next` and interpret recommendations. |
| skill-executor | `subagents/skill-executor.md` | Execute a skill by role category and capture output. |
| confidence-assessor | `subagents/confidence-assessor.md` | Assess and update confidence after each loop. |
| challenge-gate | `subagents/challenge-gate.md` | Challenge understanding before planning. |
| plan-drafter | `subagents/plan-drafter.md` | Draft the implementation plan. |
| phase-executor | `subagents/phase-executor.md` | Execute one phase of the plan. |
| implementer | `subagents/implementer.md` | Generic implementation fallback. |
| checkpoint-manager | `subagents/checkpoint-manager.md` | Maintain checkpoints and state. |

## Return contract

Each subagent should return:

1. **Summary** — what it did and what it found.
2. **Confidence impact** — whether confidence should change and why.
3. **New gaps** — any new open questions or contradictions.
4. **Artifacts produced** — paths to any files it created or updated.
5. **Recommended next action** — what the conductor should do next.

## Error handling

If a subagent reports that it cannot proceed, the conductor should:

1. Log the failure in state.
2. Decide whether to retry, try a different subagent, or stop and ask the user.
3. Never silently ignore a subagent failure.
