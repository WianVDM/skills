---
name: baseline
description: "Capture a reproducible baseline snapshot of a feature, module, route, API, or bug on a specified branch. Use when the user wants to test current app state, reproduce a bug, capture pre-change UI, or mentions 'baseline', 'reproduce', 'check the app', or 'verify UI'."
argument-hint: "Scope, ticket key, or feature/bug to baseline"
license: Proprietary
metadata:
  author: Wian van der Merwe
  version: "3.1"
  scope: global
invocation: user-invoked
disable-model-invocation: true
---

# baseline

Capture a reproducible snapshot of the current state of a feature, module, route, API, or bug on a specified branch. The snapshot becomes a trusted reference point for later work.

## Skill type

Conductor. It orchestrates a multi-step workflow and delegates scope, method, context discovery, and capture to focused workers.

## When to use

- The user wants to test or verify current app state.
- The user wants to reproduce a bug.
- The user wants to capture pre-change evidence.
- The user mentions `baseline`, `reproduce`, `check the app`, `verify UI`, `capture state`, or `snapshot`.

## Process overview

1. **Load config and detect capabilities.**
   - Done when: `.agents/config/baseline.yaml` is read, available capture methods are known, and the user is not blocked by missing required tools.

2. **Resolve scope.**
   - Done when: a single, unambiguous scope string is recorded, either from the user or from matching context reports.

3. **Resolve branch and commit.**
   - Done when: the target branch is confirmed, the current commit hash is recorded, and any branch mismatch is resolved or explicitly acknowledged by the user.

4. **Optionally consume related context.**
   - Done when: `.agents/context/` has been scanned for matching `debrief`, `handoff`, or `plan-next` reports, the consumed list is recorded, and missing reports are handled gracefully.

5. **Select capture method.**
   - Done when: a method is chosen from config, detection, or user confirmation, and a fallback is identified if the primary method may fail.

6. **Resolve target and authentication.**
   - Done when: the URL, endpoint, files, or code range is reachable, and required auth is configured without hardcoded secrets.

7. **Capture evidence.**
   - Done when: artifacts are saved under `.agents/context/baseline/{scope}-{branch}/` and a capture summary is available.

8. **Generate reports.**
   - Done when: the Markdown report is written at `.agents/context/baseline/{scope}-{branch}.md` with correct frontmatter, and the HTML gallery is generated if requested.

9. **Curate notes and finalize state.**
   - Done when: `.agents/config/baseline.yaml` is updated with new preferences or gotchas, and the workflow state file is archived or removed.

## Resumption

The skill writes a small state file at `.agents/context/baseline/.state/{scope}-{branch}.json` at each step.

- On invocation, check for a matching state file.
- If the recorded branch and commit still match the current repo, resume from the last completed step.
- If the branch or commit differs, archive the state file with a `.stale` suffix and start fresh.
- If a worker returns `needs_input`, record the pending question in the state file and resume after the user answers.
- On success, archive the state file to `-completed.json` or remove it.

## Hard stops

Stop immediately and ask the user for direction if:

- Scope is ambiguous and cannot be resolved.
- The target branch is missing or cannot be checked out.
- The target is unreachable and cannot be resolved.
- No capture method is available and the user declines a manual fallback.
- Authentication is required but cannot be resolved.

## Out of scope

- Diagnosing root cause or proposing fixes.
- Implementing changes.
- Comparing before/after states.
- Running project test suites purely for verification.
- Deploying, releasing, or modifying production systems.

## References

- [Dependencies](references/DEPENDENCIES.md)
- [Workflow](references/WORKFLOW.md)
- [Capability detection](references/CAPABILITIES.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Context reports](references/CONTEXT_REPORTS.md)
- [Authentication handling](references/AUTH.md)
- [Checklists and report templates](references/REFERENCE.md)
- [Playwright MCP setup](references/PLAYWRIGHT-SETUP.md)
- [Examples](references/EXAMPLES.md)
