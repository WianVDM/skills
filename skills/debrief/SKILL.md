---
name: debrief
description: Build a complete, validated understanding of a ticket by gathering context from issue trackers, related work, the codebase, user input, and UI baseline. Produces a structured debrief report that explains what the ticket entails, what is required, and where uncertainty remains. Use when the user mentions 'debrief', 'understand this ticket', 'get context on ticket', or provides a ticket key without clear next steps.
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "3.0"
---

# Debrief

You are a **conductor**. Your job is to coordinate focused workers so they understand a ticket thoroughly enough to explain it to the user with confidence, including what is required, what assumptions were made, and what still needs clarification.

When a worker finds something ambiguous, your first instinct is to **resolve it** — not list it and stop. Use the ticket's context, related work, the codebase, and user input to form informed assumptions. Then **challenge those assumptions** to make sure they hold. Only escalate to the user when you are genuinely unsure or when the ticket contradicts itself.

## Skill type

Conductor skill. It coordinates focused workers to investigate a ticket and produce a structured debrief report.

## When to use

- The user wants to understand a ticket.
- The user provides a ticket key without clear next steps.
- The user mentions debrief, context, or understanding a ticket.
- Before planning or implementing a ticket that needs deep investigation.

## Quick start

- Invoke with a ticket key, e.g., `PROJ-123`.
- Invoke without a key to infer the ticket from the current branch name.

Resolve the ticket key in this order:

1. **User-provided key** — use it.
2. **Current branch** — inspect for a ticket key pattern (e.g., `PROJ-123-feature-x`).
3. **Ask the user** — if the key is still unclear.

Persist the project key in config once identified.

## Process overview

1. **Setup** — load config and state, resolve the ticket key, detect available issue trackers, and create the skeleton debrief document. Delegates detection to helper scripts and `checkpoint-manager` for state initialization.

2. **Research** — delegate to `ticket-researcher` to gather the core ticket, comments, attachments, history, related tickets, and development info. The debrief document is updated immediately.

3. **Resolve ambiguities** — delegate to `code-explorer` to investigate the codebase and to `assumption-challenger` to validate assumptions. Form, rate, and revise assumptions until they hold or must be escalated.

4. **Verify state** — invoke the `baseline` skill when the ticket involves verifiable UI, API, or code state. Surface questions to the user, retry on `needs_input`, and never silently skip baseline.

5. **Synthesize** — delegate to `synthesis-writer` to finalize the debrief report, then ask `checkpoint-manager` to validate all phases are complete and consistent.

For the detailed 13-step process, see [references/WORKFLOW.md](references/WORKFLOW.md).

## Incremental output and checkpointing

Write the debrief document incrementally, not only at the end. Start with a skeleton marked `<!-- STATUS: pending -->`, then replace each marker with `<!-- STATUS: completed -->` as sections finish. The state file tracks phase completion and current focus.

After every subagent return and after any context compaction, update the debrief document, ask `checkpoint-manager` to refresh the phase checklist and focus, then re-read both files before deciding the next action.

See [references/CHECKPOINTING.md](references/CHECKPOINTING.md) for phase definitions and self-validation prompts.

## Recontextualization after compaction

If the session context is compacted, the agent must not guess where it left off. Instead:

1. Read `.agents/context/debrief/{key}/state.md`.
2. Read `.agents/context/debrief/{key}-{slug}.md`.
3. Ask the `checkpoint-manager` to summarize: completed phases, pending phases, current focus, and recommended next action.
4. Resume from the first pending phase.
5. Do not restart completed phases unless new information contradicts them.

## Context graph

The skill gathers evidence from multiple sources:

| Source | What to capture |
|--------|-----------------|
| Core ticket | Summary, description, acceptance criteria, status, priority |
| Related tickets | Parent, child, linked, duplicated, referenced |
| Development info | PRs, branches, commits |
| Codebase | Files mentioned, related patterns, similar features |
| User input | Clarifications, screenshots, notes |
| Baseline | UI evidence, reproduction results |

Record each source in state with a relevance score and what it contributed. See [references/CONTEXT_REPORTS.md](references/CONTEXT_REPORTS.md).

## Assumption handling

- Form explicit assumptions for every ambiguity.
- Rate each assumption's confidence and alignment.
- Challenge assumptions by searching for disproof, not confirmation.
- Escalate only assumptions with low confidence or direct contradictions.

See [references/ASSUMPTIONS.md](references/ASSUMPTIONS.md).

## Baseline integration

`baseline` is a recommended skill dependency. A baseline is required by default for tickets that involve verifiable UI, API, or code state, because it provides ground-truth evidence of current state.

Never silently skip baseline. If baseline cannot proceed due to an auth prompt, unreachable target, or missing tool, surface the issue to the user and ask how to proceed. If the ticket clearly does not involve verifiable state, consult the user before deciding to skip.

See [references/BASELINE-INTEGRATION.md](references/BASELINE-INTEGRATION.md).

## Confidence levels

Rate overall debrief confidence honestly:

| Level | Range | Meaning |
|-------|-------|---------|
| **Red** | 0-59% | Too many unresolved ambiguities or contradictions. |
| **Yellow** | 60-84% | Some assumptions made, documented and reasonable. |
| **Green** | 85-100% | Clear understanding with confident resolutions. |

## Output location

Canonical outputs live at:

```text
.agents/context/debrief/
├── {key}-{slug}.md
└── {key}/
    └── state.md
```

See [references/CONTEXT_REPORTS.md](references/CONTEXT_REPORTS.md) for report schema and freshness rules.

## Hard stops

Stop and consult the user if:

- No ticket key can be resolved.
- No issue tracker or manual context is available.
- The ticket contradicts itself or related work.
- Baseline is required for this ticket but cannot proceed, and the user does not approve skipping.
- Confidence remains Red after exhausting available evidence.

## References

- [Dependencies](references/DEPENDENCIES.md)
- [Context reports](references/CONTEXT_REPORTS.md)
- [Workflow detail](references/WORKFLOW.md)
- [Worker contract](references/WORKER_CONTRACT.md)
- [Versioning](references/VERSIONING.md)
- [Capability detection](references/CAPABILITIES.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Issue tracker adapters](references/trackers/)
- [Assumption handling](references/ASSUMPTIONS.md)
- [Baseline integration](references/BASELINE-INTEGRATION.md)
- [Checkpointing and incremental output](references/CHECKPOINTING.md)
- [Detailed reference](references/REFERENCE.md)
- [Examples](references/EXAMPLES.md)
- [Validation](references/VALIDATION.md)

## Out of scope

- Recommending the next skill to run.
- Implementing fixes.
- Writing code.
- Running project test suites.
