---
skill: handoff
version: "3.0"
timestamp: 2026-07-03T00:00:00Z
auditor: write-a-skill
scope: global
---

# Handoff audit (v3.0 stripped)

## Files audited

- `skills/handoff/SKILL.md`
- `skills/handoff/README.md`
- `skills/handoff/scripts/handoff-helper.py`

## Findings

| Criterion | Rating | Notes |
|---|---|---|
| A1 | Green | `handoff` matches directory. |
| A2 | Green | Description is under 1024 chars and states trigger. |
| A3 | Green | Leading word "Snapshot" front-loaded. |
| A4 | Green | `invocation: user-invoked` and `disable-model-invocation: true` declared. |
| B1 | Green | Single objective: snapshot session state. |
| B2 | Green | Purpose is clear. |
| B3 | Green | Triggers in description. |
| B4 | Green | Out-of-scope concise and explicit. |
| B5 | Green | Standalone with helper script. |
| C1 | Green | Instruction-heavy; workflow first. |
| C2 | Green | Step 5 has a strong, checkable criterion. |
| C3 | Green | Criterion is checkable. |
| C4 | Green | Leading word "Snapshot" used. |
| C5 | Green | "Snapshot, not summary" explains the why. |
| C6 | Green | Negations paired with positives via out-of-scope. |
| C7 | Green | No vague guideline soup. |
| C8 | Green | Workflow is stated, not a manual. |
| C9 | Green | No hidden hybrid. |
| C10 | Green | No no-op lines. |
| D1 | Green | SKILL.md is the contract; README is minimal reference. |
| D2 | Green | Related concepts grouped. |
| D3 | Green | SKILL.md is extremely lean. |
| D4 | Green | No sediment. |
| D5 | Green | No duplication. |
| D6 | Green | SKILL.md and README.md present. |
| E1 | Green | `scope: global`. |
| E2 | Yellow | `/handoff` slash syntax is harness-specific; intentional. |
| E3 | Green | No hardcoded project paths. |
| E4 | Green | Context directory detected. |
| E5 | Green | Dependencies listed. |
| E6 | Green | Failure modes explicit. |
| F5 | Green | Overwrites avoided by sequence increment. |
| G1 | Green | State/output locations documented. |
| G2 | Green | Schema documented in README. |
| G5 | Green | Report schema documented. |
| H5 | Green | Deterministic logic in helper script. |
| H6 | Green | Script is safe and isolated. |
| I1 | Green | Dependencies documented. |
| I5 | Green | No premature abstraction. |
| J1 | Green | No secrets. |
| J2 | Green | No silent overwrites. |
| J5 | Green | Writes only to context directory. |
| K3 | Green | Version bumped to 3.0. |
| K1, K2, K5 | Yellow | Evals and review cadence planned but not implemented. |

## Blockers

None.

## Verdict

v3.0 is a stripped-down, load-bearing skill. SKILL.md is now a concise executable contract; README is a minimal reference. The handoff quality is guarded by the "snapshot, not summary" framing and the Step 5 tightening criterion. No Red blockers. Evals and review cadence remain to be implemented after real-world use.
