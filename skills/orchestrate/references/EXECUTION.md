# Execution

Rules for executing an approved plan.

## Before the first phase

1. Save the confirmed plan to `.agents/context/orchestrate/{key}/plan.md`.
2. Record the confirmation decision in state.

## Start of each phase

1. **Recontextualize** — read plan.md, latest checkpoint, state.md, decisions.md, assumptions.md, and current phase contract.
2. **Git status check** — detect any deviation from expected branch state.
3. **Summarize** — state current phase, next checklist item, what should already be done, and any deviations.
4. **Self-consistency check** — answer in `## Decisions`:
   - What is the current phase?
   - What is the next checklist item?
   - What should I NOT do in this phase?
   - Are any open questions blocking this item?

## During the phase

1. Generate the phase contract before writing code.
2. Execute the checklist sequentially.
3. Mark checklist items complete as you go.

## End of each phase

1. **Validate** — run the first available verification skill from config.
2. If UI changed, run UI verification.
3. Update state with validation results.
4. If validation fails:
   - Interactive: stop, present findings, ask user.
   - Auto: attempt auto-fix once, log attempt, stop if still failing.
5. **Handoff** — run the configured checkpoint skill to create the next checkpoint.

## If execution reveals new gaps

1. Stop execution immediately.
2. Update state: lower confidence, add open questions, document contradiction.
3. Return to the understanding loop.
4. Do not patch over uncertainty.

## Phase deviation recovery

If the working tree does not match the latest checkpoint:

1. Announce the deviation and show the diff.
2. If small and explainable, reconcile and log a decision.
3. If large or unexplained, stop, hand off the deviation, and return to the loop or ask the user.

## Auto vs interactive

| Situation | Interactive | Auto |
|-----------|-------------|------|
| Drafting plan | Present plan, wait for confirmation | Save plan, log "proceeding on auto", continue |
| New gap discovered | Stop, tell user, ask whether to re-loop | Return to loop, run skills, log decisions |
| Validation FAIL | Stop, present findings | Attempt auto-fix once, stop if still failing |

In auto mode, every choice that would have required user input must be logged in `## Decisions`.
