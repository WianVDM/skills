# Workflow

This document is the detailed reference for the `debrief` skill's 13-step workflow. The main [SKILL.md](../SKILL.md) uses a compressed, five-phase overview; use this file when you need the full step-by-step process for implementation or troubleshooting.

The 13 steps map to the eight phases defined in [CHECKPOINTING.md](CHECKPOINTING.md). The phase mapping is included after the process overview.

---

## 13-step process

1. **Load config and state** — read `.agents/config/debrief.yaml` and `.agents/context/debrief/{key}/state.md` if they exist.
2. **Resolve ticket key** — from user input, branch name, or previous state.
3. **Detect context sources** — identify available issue trackers, development info sources, and codebase access. See [CAPABILITIES.md](CAPABILITIES.md).
4. **Resolve tracker** — if ambiguous, ask the user and persist the choice.
5. **Create skeleton debrief** — write `.agents/context/debrief/{key}-{slug}.md` with section headers and status markers. See [CHECKPOINTING.md](CHECKPOINTING.md).
6. **Research ticket** — delegate to `ticket-researcher`. Gather the core ticket, comments, attachments, history, related tickets, and development info.
7. **Update debrief** — immediately write research results into the debrief document and update the phase checklist.
8. **Ask checkpoint manager** — delegate to `checkpoint-manager` to update state, verify phase completion, and report current focus.
9. **Resolve ambiguities** — for each ambiguity:
   - Delegate code exploration to `code-explorer`.
   - Form explicit assumptions.
   - Delegate assumption challenging to `assumption-challenger`.
   - Revise, confirm, or escalate based on challenge results.
   - Update the debrief document and phase checklist after each step.
10. **Capture baseline** — delegate to the `baseline` skill or a baseline subagent. Surface any user questions to the user. See [BASELINE-INTEGRATION.md](BASELINE-INTEGRATION.md).
11. **Synthesize** — delegate to `synthesis-writer` to finalize incomplete sections of the debrief document.
12. **Final validation** — ask `checkpoint-manager` to verify all phases are complete and consistent.
13. **Present findings** — give the user a human-readable summary with confidence, assumptions, and any escalated items.

---

## Mapping to the eight phases

| Step(s) | Phase | Name | Output |
|---------|-------|------|--------|
| 1–4 | 1 | Resolve ticket key and load context | Project key resolved, config loaded |
| 5–7 | 2 | Fetch ticket + related data | Debrief sections: Metadata, Discussion Summary, Attachments, Related Tickets, Development Context |
| 7 | 3 | Build context graph | State: Context Graph populated |
| 9 (first part) | 4 | Identify ambiguities | State: Ambiguities list populated |
| 9 (code exploration) | 5 | Resolve ambiguities via code exploration | Debrief section: Codebase Evidence; State: Ambiguities updated |
| 9 (challenging) | 6 | Challenge assumptions | Debrief section: Assumptions Resolved; State: Ambiguities updated |
| 10 | 7 | Run baseline | Debrief section: Baseline Status; State: Baseline Status updated |
| 11–13 | 8 | Synthesize final debrief | All sections marked complete, frontmatter updated |

---

## Incremental output and checkpointing

The debrief document is written incrementally, not produced only at the end. This protects against context compaction and makes the current state inspectable at any time.

At the start, create a skeleton document with each section marked `<!-- STATUS: pending -->`. As each section is completed, replace the marker with `<!-- STATUS: completed -->` and fill the content. The state file tracks which phases are complete, which are in progress, and what the current focus is.

After every subagent returns, and after any context compaction:

1. Update the debrief document with the new findings.
2. Ask the `checkpoint-manager` to update the phase checklist and current focus.
3. Re-read the state file and debrief document before deciding the next action.

See [CHECKPOINTING.md](CHECKPOINTING.md) for phase definitions and self-validation prompts.

---

## Recontextualization after compaction

If the session context is compacted, the agent must not guess where it left off. Instead:

1. Read `.agents/context/debrief/{key}/state.md`.
2. Read `.agents/context/debrief/{key}-{slug}.md`.
3. Ask `checkpoint-manager` to summarize: completed phases, pending phases, current focus, and recommended next action.
4. Resume from the first pending phase.
5. Do not restart completed phases unless new information contradicts them.

---

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

Record each source in state with a relevance score and what it contributed.

---

## Assumption handling

- Form explicit assumptions for every ambiguity.
- Rate each assumption's confidence and alignment.
- Challenge assumptions by searching for disproof, not confirmation.
- Escalate only assumptions with low confidence or direct contradictions.

See [ASSUMPTIONS.md](ASSUMPTIONS.md).

---

## Baseline integration

Baseline is recommended for most tickets because it provides ground-truth evidence of current state. However, if the ticket clearly does not involve a verifiable UI, API, or code state, or if baseline cannot proceed, consult the user before skipping it. Never silently skip a baseline because of an auth prompt, unreachable target, or missing tool.

See [BASELINE-INTEGRATION.md](BASELINE-INTEGRATION.md).

---

## Confidence levels

Rate overall debrief confidence honestly:

| Level | Range | Meaning |
|-------|-------|---------|
| **Red** | 0-59% | Too many unresolved ambiguities or contradictions. |
| **Yellow** | 60-84% | Some assumptions made, documented and reasonable. |
| **Green** | 85-100% | Clear understanding with confident resolutions. |

---

## Output location

Canonical outputs live at:

```text
.agents/context/debrief/
├── {key}-{slug}.md
└── {key}/
    └── state.md
```

---

## Hard stops

Stop and consult the user if:

- No ticket key can be resolved.
- No issue tracker or manual context is available.
- The ticket contradicts itself or related work.
- Baseline is required for this ticket but cannot proceed, and the user does not approve skipping.
- Confidence remains Red after exhausting available evidence.
