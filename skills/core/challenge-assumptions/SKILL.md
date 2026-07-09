---
name: challenge-assumptions
description: "Stress-test a list of assumptions by searching for disproof signals across provided evidence. Use when a skill needs to avoid confirmation bias."
version: 1.0.0
license: Proprietary
invocation: model-invoked
metadata:
  author: Wian van der Merwe
  tags: [assumptions, skepticism, validation, building-block, core]
allowed-tools:
  - read
  - bash
---

# challenge-assumptions

## Identity

`challenge-assumptions` is a deterministic building-block skill that stress-tests a caller-supplied list of assumptions by searching for disproof signals across the provided evidence. It is designed to counter confirmation bias: instead of looking for confirmation, it looks for contradictions.

## Purpose and type

- **Type**: Building-block skill / deterministic script wrapper.
- **Purpose**: Take explicit assumptions and available evidence, search for contradictions, and report whether each assumption holds, is challenged, or remains inconclusive.
- **Judgment**: None. The script uses deterministic keyword/phrase matching; the caller decides whether and how to adjust confidence.

## In scope

- Read a list of assumptions from the caller. Each assumption includes `text` and optional `basis`.
- Read evidence from the caller. Evidence is a dictionary of named evidence sources (e.g., `ticket_data`, `codebase_evidence`, `relationships`, `comments`, `adrs`).
- For each assumption, derive a small set of disproof signals (negated phrases, contradiction markers, and alternative phrasing) from the assumption text.
- Search the provided evidence for those disproof signals using simple keyword/phrase matching.
- Report each assumption as:
  - `holds` — no disproof signals were found in the evidence.
  - `challenged` — at least one disproof signal was found in the evidence.
  - `inconclusive` — the assumption was empty or could not be processed.
- Return a structured JSON envelope with the challenged assumptions and references to the evidence sources that contradicted them.

## Out of scope

- Do not form new assumptions. Only challenge assumptions provided by the caller.
- Do not fetch additional evidence or context beyond what the caller provides.
- Do not ask the user questions. If required inputs are missing, return `status: needs_input`.
- Do not change confidence ratings, make decisions, or recommend actions. Only report findings.
- Do not use LLM judgment or semantic reasoning. Matching is keyword/phrase based.

## When to use

- A conductor such as `debrief` has formed assumptions and needs to stress-test them before accepting them.
- Any skill that forms explicit assumptions wants to avoid confirmation bias by searching for disproof.
- The user asks: *"What could disprove this assumption?"* or *"Challenge these assumptions."*

## Input / output contract

### Input

The skill accepts a JSON object via stdin to `scripts/challenge-assumptions.py`.

```json
{
  "assumptions": [
    {
      "text": "Token refresh happens in auth.guard.ts.",
      "basis": "Code in auth.guard.ts contains refresh logic; no interceptor was found in a quick search."
    }
  ],
  "evidence": {
    "codebase_evidence": "src/app/interceptors/refresh.interceptor.ts handles token refresh before the guard runs.",
    "ticket_comments": "The issue is not in the guard; the interceptor refresh logic is missing a timeout.",
    "adrs": "ADR-12: Authentication flows must use a refresh interceptor, not the guard."
  }
}
```

| Field | Required | Default | Description |
|---|---|---|---|
| `assumptions` | yes | — | List of assumptions to challenge. Each item has `text` (required) and optional `basis`. |
| `evidence` | no | `{}` | Dictionary of named evidence sources. Values are strings or lists of strings. |
| `max_signals` | no | `10` | Maximum number of disproof signals to generate per assumption. |
| `context_window` | no | `10` | Number of words around a matched phrase to check for contradiction markers. |
| `proximity` | no | `3` | Maximum word distance between a contradiction marker and an assumption phrase before the marker is considered adjacent. |

### Output

```json
{
  "status": "complete",
  "assumptions": [
    {
      "text": "Token refresh happens in auth.guard.ts.",
      "status": "challenged",
      "notes": "Found contradiction in codebase_evidence: 'refresh.interceptor.ts handles token refresh' near the assumption phrase.",
      "disproof_refs": ["codebase_evidence", "adrs"],
      "disproof_signals_searched": ["not auth.guard.ts", "not in auth.guard.ts", "interceptor handles", "refresh interceptor"],
      "evidence_found": [
        "codebase_evidence: 'src/app/interceptors/refresh.interceptor.ts handles token refresh'"
      ]
    }
  ]
}
```

| Field | Description |
|---|---|
| `status` | `complete`, `needs_input`, `blocked`, or `partial`. |
| `assumptions` | Parallel list of assumptions with challenge results. |
| `text` | The original assumption text. |
| `status` | `holds`, `challenged`, or `inconclusive`. |
| `notes` | Human-readable explanation of the challenge result. |
| `disproof_refs` | List of evidence source keys that contained disproof signals. |
| `disproof_signals_searched` | Signals generated and searched for this assumption. |
| `evidence_found` | Exact or near-exact evidence snippets that challenged the assumption. |

### Status values

| Status | Meaning | Caller action |
|---|---|---|
| `complete` | All assumptions processed and results returned. | Use results to adjust confidence or escalate. |
| `partial` | Some assumptions processed; an error or limit prevented full processing. | Review assumptions that returned `inconclusive`. |
| `needs_input` | Required input is missing (e.g., no `assumptions` provided). | Surface to user or provide assumptions. |
| `blocked` | Unexpected error prevented processing. | Investigate. |

## Lazy loading

`challenge-assumptions` is only invoked after assumptions are formed. It does not run if there are no assumptions to challenge. The script itself is stateless and performs no eager initialization.

## Dependencies

See `references/DEPENDENCIES.md` for required tools, binaries, and skills.

## Example usage by a conductor

```text
Run challenge-assumptions with assumptions [{"text": "Token refresh happens in auth.guard.ts.", "basis": "refresh logic found in guard"}] and evidence from ticket comments, codebase_evidence, and adrs.
```

```text
Run challenge-assumptions with the assumptions formed in the previous step and the evidence gathered by research-ticket and explore-code.
```

## Implementation notes

- The deterministic entry point is `scripts/challenge-assumptions.py`.
- Disproof signals are natural-language negations and synonyms derived from the assumption text (e.g., "X is not in Y", "Z handles X"), not literal prefixes of the whole sentence.
- Matching is case-insensitive and punctuation-insensitive.
- A contradiction is reported only when a contradiction marker appears within `proximity` words of an assumption phrase or its negation in the evidence.
- No LLM calls are made inside the script.

## Security and safety

- Read-only: the script only inspects evidence provided by the caller.
- Does not access the filesystem, network, or issue trackers unless the caller includes them in `evidence`.
- Does not mutate project state or ask the user questions.
- No secrets are read or transmitted.
