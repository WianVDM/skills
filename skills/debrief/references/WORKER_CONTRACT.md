# Worker Contract

All `debrief` subagents return their findings using this standard contract. The main skill reads the returned body, updates the debrief document and state file, and decides what to do next.

---

## Status values

Every worker response must include a `status` field in the frontmatter.

| Status | Meaning | Next action for main skill |
|--------|---------|---------------------------|
| `complete` | The worker finished its task and all expected outputs are present. | Incorporate findings and continue to the next phase. |
| `partial` | The worker finished some of its task but missing data, scope limits, or recoverable issues remain. | Note gaps, decide whether to retry, escalate, or proceed with reduced confidence. |
| `needs_input` | The worker needs a decision or information from the user (e.g., credentials, scope, confirmation). | Surface the question to the user. Do not let the worker ask the user directly. |
| `blocked` | The worker cannot proceed because of an unrecoverable error (e.g., tracker unavailable, file system error). | Stop the current phase, report the blocker, and present options to the user. |

---

## Artifacts list

Workers may produce artifacts such as:

- `debrief_document` — path to the `.agents/context/debrief/{key}-{slug}.md` file (for `synthesis-writer`).
- `state_file` — path to the `.agents/context/debrief/{key}/state.md` file (for `checkpoint-manager`).
- `context_graph` — table of sources with relevance and contribution.
- `findings` — structured evidence or conclusions.
- `ambiguities` — list of unresolved or resolved ambiguities.
- `assumptions` — list of assumptions with confidence and basis.
- `baseline_status` — status and notes from baseline integration.

If a worker writes a file directly, it must return the path in the `artifacts` list. If it only returns structured text, it must still include an `artifacts` list, even if it is empty.

---

## Body sections

A worker return should include these sections when relevant:

1. **Summary** — one-paragraph overview of what was done and what was found.
2. **Findings** — the primary output of the worker (e.g., context graph, codebase evidence, assumption challenges, status summary).
3. **Decisions made** — any decisions the worker made on its own, with reasoning.
4. **Open questions** — questions that remain unresolved but do not require the user to answer immediately.
5. **Blockers** — anything that prevented full completion. This is the only section that should be populated when `status: blocked`.

---

## Worker rules

- **Workers do not ask the user directly.** If a worker needs user input, it must return `status: needs_input` and include the question in the `Open questions` or `Blockers` section. The main skill owns all user interaction.
- **Workers do not make phase decisions.** They return findings; the main skill decides whether to proceed, retry, or escalate.
- **Workers do not write to the debrief document unless explicitly instructed.** Most workers return findings and let the main skill incorporate them. `synthesis-writer` and `checkpoint-manager` are exceptions when their role requires file updates.
- **Workers must be honest about confidence.** A `partial` return is preferable to inventing missing data.
- **Workers must use the canonical schemas.** Return data in the formats documented in [REFERENCE.md](REFERENCE.md) and [CONTEXT_REPORTS.md](CONTEXT_REPORTS.md).

---

## Escalation rules

Escalate to the main skill (and ultimately to the user) when:

- A required source is unavailable and no fallback exists (`status: blocked`).
- The ticket or request contradicts itself or previously gathered evidence.
- The user must choose between mutually exclusive interpretations.
- The worker needs credentials, authentication, or environment setup to continue.
- The worker's task scope is unclear or exceeds its mandate.

The main skill must present escalated items to the user in natural language, with the worker's exact question and any assumptions already formed.
