---
name: baseline
description: "Capture a reproducible snapshot of a feature, module, route, API, or bug. Invoked by baseline, reproduce, verify UI, check the app, capture state, or snapshot."
argument-hint: "Scope, ticket key, or feature/bug to baseline"
invocation: model-invoked
---

# baseline

Capture a reproducible snapshot of the current state of a feature, module, route, API, or bug on a specified branch. The snapshot becomes a trusted reference point for later work.

## Skill type

Conductor. Delegates scope, context, method selection, and capture to focused workers.

## When to use

- The user says `baseline`, `reproduce`, `check the app`, `verify UI`, `capture state`, or `snapshot`.
- The user wants to test or verify current app state.
- The user wants to reproduce a bug.
- The user wants to capture pre-change evidence.

## Process overview

1. **Load config and detect required capabilities.** Read `{config_dir}/baseline.yaml` and shared config. Check that `git` and `python3` are available. Stop if a required capability is missing and explain what is required.

2. **Resolve scope and branch.** Delegate to `scope-resolver`. If scope is ambiguous, stop and ask. Confirm before switching branches. Record the commit hash.

3. **Consume related context.** Delegate to `context-scout`. Read matching reports from `{context_dir}/`, excluding baseline outputs. Handle missing reports gracefully.

4. **Select capture method.** Delegate to `method-selector`. Respect user preferences from config. Ask when multiple methods are viable. Identify a fallback.

5. **Resolve tooling for the selected method.** Check whether the project has tooling that supports the selected method. If not, explain the gap and offer: configure a recommended tool, switch to an alternative method, or use manual fallback. Persist the chosen tooling path only after explicit confirmation.

6. **Resolve target and authentication.** Confirm the target URL, endpoint, or files are reachable. Resolve auth without storing secrets in config.

7. **Capture evidence.** Delegate to `capture-worker`. Gather screenshots, logs, responses, or file contents. Record enough findings for a one-sentence summary.

8. **Generate reports.** Write the canonical Markdown report and optional HTML gallery to `{context_dir}/baseline/`. Include all required frontmatter.

9. **Curate notes.** Update `{config_dir}/baseline.yaml` with new notes and tooling preferences, but never silently overwrite existing values. Archive or remove the state file.

## Resumption

The skill writes a state file at `{context_dir}/baseline/.state/{scope}-{branch}.json` after each step.

- Resume from the last step if branch and commit still match.
- Archive stale state with `.stale` and start fresh if they differ.
- Record pending `needs_input` questions and resume after the user answers.
- On success, archive the state to `-completed.json` or remove it.

## Hard stops

Stop and ask for direction if:

- Scope is ambiguous.
- The target branch is missing or unreachable.
- The target is unreachable.
- A required capability (`git` or `python3`) is missing.
- The selected capture method has no available tooling and the user declines all alternatives (manual fallback included).
- Authentication is required but cannot be resolved.

## Out of scope

- Diagnosing root cause or proposing fixes; instead, record observed behavior and stop.
- Implementing changes; instead, capture state and hand off to the appropriate skill.
- Comparing before/after states; instead, produce the snapshot that other skills compare.
- Running project tests purely for verification; instead, use tests only as a capture method when relevant.
- Deploying or modifying production systems.
- Installing packages or binaries without explicit user approval; the skill may suggest or generate config, but it must not run installers silently.

## References

- [Dependencies](references/DEPENDENCIES.md)
- [Workflow](references/WORKFLOW.md)
- [Capability detection](references/CAPABILITIES.md)
- [Tooling catalog](references/TOOLING.md)
- [Configuration and notes](references/CONFIG_PATTERN.md)
- [Context reports](references/CONTEXT_REPORTS.md)
- [Authentication handling](references/AUTH.md)
- [Checklists and report templates](references/REFERENCE.md)
- [Examples](references/EXAMPLES.md)
