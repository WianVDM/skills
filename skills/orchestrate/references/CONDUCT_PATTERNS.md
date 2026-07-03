# Conduct Patterns

Common patterns for the conductor loop.

## Pattern 1: Fresh bug

Context: New bug report, debrief and baseline exist.

1. Load context.
2. Run `plan-next`.
3. Run `diagnose` to reproduce and find root cause.
4. If root cause is in an unexpected subsystem, re-run `plan-next`.
5. Run `grill-with-docs` to align with domain model and ADRs.
6. Challenge gate.
7. Draft plan: reproduce → fix → verify.

## Pattern 2: Ambiguous feature

Context: Requirements are unclear or contradictory.

1. Load context.
2. Run `grill-me` to surface missing requirements and edge cases.
3. Run `prototype` to explore design options.
4. Run `grill-with-docs` to align with domain language.
5. Challenge gate.
6. Draft plan: requirements → design → implement → verify.

## Pattern 3: UI-only change

Context: Visual or interaction change, baseline exists.

1. Load context.
2. Run `baseline` to capture current UI.
3. Run `plan-next` to confirm scope.
4. Run `grill-me` briefly for edge cases.
5. Challenge gate (can be lightweight).
6. Draft plan: implement → baseline diff → verify.

## Pattern 4: Large architectural change

Context: Cross-module refactor or new subsystem.

1. Load context.
2. Run `zoom-out` for system context.
3. Run `plan-next`.
4. Run `grill-with-docs` for ADR alignment.
5. Run `prototype` if the design is uncertain.
6. Multiple challenge gates.
7. Draft plan with many small phases and strong verification.

## Pattern 5: PR feedback follow-up

Context: Existing PR has review comments.

1. Load context.
2. Run `pr-report` to normalize feedback.
3. Run `plan-next` to prioritize.
4. Run `diagnose` or `grill-with-docs` as needed.
5. Challenge gate.
6. Draft plan: address feedback → verify → update PR.
