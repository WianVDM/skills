---
name: baseline
description: "Capture a reproducible baseline snapshot of the current state of a feature, module, route, API, or bug on a specified branch. Triggers: test or verify app state; reproduce a bug; capture pre-change evidence; or mention `baseline`, `reproduce`, `check the app`, `verify UI`, `capture state`, or `snapshot`."
argument-hint: "Scope, ticket key, or feature/bug to baseline"
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "1.0.0"
  scope: global
invocation: user-invoked
disable-model-invocation: true
---

# baseline

Capture a reproducible snapshot of the current state of a feature, module, route, API, or bug on a specified branch. The snapshot becomes a trusted reference point for later work.

## Skill type

Conductor. Delegates scope, context, method selection, and capture to focused workers.

## When to use

- Test or verify current app state.
- Reproduce a bug.
- Capture pre-change evidence.
- The user mentions `baseline`, `reproduce`, `check the app`, `verify UI`, `capture state`, or `snapshot`.

## Process overview

1. **Load config and detect capabilities.**
   - Done when: config is read and available capture methods are known.

2. **Resolve scope.**
   - Done when: an unambiguous scope is recorded from the user or matching context reports.

3. **Resolve branch and commit.**
   - Done when: branch is confirmed, commit is recorded, and any mismatch is resolved with the user.

4. **Consume related context.**
   - Done when: `.agents/context/` is scanned for matching reports, baseline outputs are excluded, and missing reports are handled gracefully.

5. **Select capture method.**
   - Done when: a method is chosen from config, detection, or user confirmation, with a fallback identified.

6. **Resolve target and authentication.**
   - Done when: the target is reachable and auth is configured without hardcoded secrets.

7. **Capture evidence.**
   - Done when: artifacts are saved and findings are sufficient for a one-sentence summary.

8. **Generate reports.**
   - Done when: the report is written with correct frontmatter, including `summary` and type-appropriate `reproducible`, and HTML is generated if requested.

9. **Curate notes.**
   - Done when: config is updated with new notes and the state file is archived or removed.

## Resumption

The skill writes a state file at `.agents/context/baseline/.state/{scope}-{branch}.json` after each step.

- Resume from the last step if branch and commit still match.
- Archive stale state with `.stale` and start fresh if they differ.
- Record pending `needs_input` questions and resume after the user answers.
- On success, archive the state to `-completed.json` or remove it.

## Hard stops

Stop and ask for direction if:

- Scope is ambiguous.
- The target branch is missing or unreachable.
- The target is unreachable.
- No capture method is available and the user declines manual fallback.
- Authentication is required but cannot be resolved.

## Out of scope

- Diagnosing root cause or proposing fixes.
- Implementing changes.
- Comparing before/after states.
- Running project tests purely for verification.
- Deploying or modifying production systems.

## References

- [Dependencies](references/DEPENDENCIES.md)
- [Workflow](references/WORKFLOW.md)
- [Capability detection](references/CAPABILITIES.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Context reports](references/CONTEXT_REPORTS.md)
- [Authentication handling](references/AUTH.md)
- [Checklists and report templates](references/REFERENCE.md)
- [Examples](references/EXAMPLES.md)
