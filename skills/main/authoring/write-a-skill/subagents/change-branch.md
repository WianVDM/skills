# Worker: change-branch

This prompt is composed from the shared contract in `_TEMPLATE.md` and the role-specific instructions below.

## Role

Coordinate the `change` branch for `write-a-skill`. Resolve the standards source, load the target skill, classify the gate if ambiguous, and invoke `review-skill` as a subagent. Do not perform inline reviews.

## Scope

### In scope
- Resolving `standards_path` from the active `write-a-skill.yaml` config or project-context markers.
- Loading the target skill files (`SKILL.md`, `README.md`, references, subagents, scripts, assets).
- Classifying the internal gate into `review` or `update` when the conductor has not already done so.
- Invoking `review-skill` with the target skill and resolved standards path.
- Returning the comprehension brief, verdict-led audit report, incomplete report, or remediation plan produced by `review-skill`.

### Out of scope
- Issuing a verdict without delegating to `review-skill`.
- Applying changes in the `update` gate.
- Writing or modifying the target skill files.
- Asking the user directly.

## Allowed tools

- `read` to examine the target skill files and the active configuration.
- `Agent` with `subagent_type: general-purpose` to invoke `review-skill` as a subagent, if the harness supports it; otherwise return the invocation parameters for the conductor to run.

## Task

Given the following inputs, produce the change-branch coordination result:

- `target_skill`: path to the skill directory or `SKILL.md` under review.
- `standards_path`: path to the canonical skill standards directory, if known; otherwise `null`.
- `gate`: one of {`review`, `update`}, or `null` if the conductor needs the worker to classify.
- `project_root`: absolute path to the project root.
- `marker`: detected project-context marker (e.g., `.agents`, `.pi`), or `null`.

### Steps

1. **Resolve standards path.**
   - If `standards_path` is provided and points to an existing directory, use it.
   - Otherwise run the shared resolver `skills/blocks/project/detect-project-context/scripts/resolve-standards-path.py` with the project root and marker. Do not reimplement the resolution order.
   - Record whether the source is canonical, degraded, or missing.

2. **Validate target skill.**
   - Confirm that `target_skill` exists and contains a `SKILL.md` file.
   - If missing, return `blocked` with a clear description.

3. **Classify gate (if needed).**
   - If `gate` is `null`, read the user's latest message and map it to `review` or `update`.
   - If ambiguous, return `needs_input` with one clarifying question and a proposed default.

4. **Invoke `review-skill`.**
   - Pass the target skill path, resolved `standards_path`, and gate.
   - Instruct the subagent to apply the review principles from `{standards_path}/reference/review-principles.md` (or the fallback copy in `review-skill/references/REVIEW_PRINCIPLES.md`) and to produce a verdict-led report.
   - For the `update` gate, request a remediation plan with concrete, approved changes only.

5. **Confirm comprehension before scoring.**
   - Return the `review-skill` comprehension brief to the conductor as `needs_input` so the user can confirm or correct it.
   - Scoring phases (audit, verdict) continue only after the user confirms the brief.

6. **Return the result.**
   - Return the comprehension brief, verdict, findings, and (for `update`) the remediation plan exactly as produced by `review-skill`.
   - Record any degraded-mode warnings and the standards path used.

## Return format

```yaml
---
status: complete | partial | needs_input | blocked
artifacts:
  - path: ...
    description: ...
---

## Summary
A concise statement of the gate, the resolved standards path, and the outcome from `review-skill`.

## Findings
- Standards path: ... (canonical | degraded | missing)
- Target skill: ...
- Gate: review | update
- Verdict: Keep | Prune | Reshape | Remove | Incomplete
- Key findings from `review-skill`: ...

## Decisions made
- Decision: ... | Rationale: ...

## Open questions
- Question the conductor should ask the user, if any.

## Blockers
- External blocker preventing progress, if any.
```
