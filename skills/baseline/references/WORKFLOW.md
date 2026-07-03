# Baseline Workflow

Detailed workflow for the `baseline` skill.

## 0. Check for existing state and resume if fresh

Before starting, check `.agents/context/baseline/.state/{scope}-{branch}.json`.

- If it exists and the recorded `branch` and `commit` still match the current repo, resume from `current_step`.
- If it is stale (branch or commit differs), archive it with a `.stale` suffix and start fresh.
- If a worker returned `needs_input`, present the recorded question and resume after the user answers.

After this step, write the state file with `current_step: 1`.

## 1. Load config

Read `.agents/config/baseline.yaml` and `.agents/config/shared.yaml` if they exist.

After this step, update the state file with `current_step: 1`.

## 2. Detect capabilities

Identify available capture methods. See [CAPABILITIES.md](CAPABILITIES.md). Methods include UI automation, API calls, project tests, code snapshots, or manual fallback.

After this step, update the state file with `current_step: 2`.

## 3. Resolve scope

Determine what to baseline:

- If the user provided a ticket key, feature, module, or bug description, use it.
- If no scope is provided, scan `.agents/context/` for recent reports (e.g., `debrief`, `handoff`, `plan-next`) that might imply a scope.
- If scope remains ambiguous, stop and ask the user.

After resolving scope, update the state file with `scope` and `current_step: 3`.

## 4. Resolve branch and commit

- Confirm the target branch. If none is specified, use the current branch.
- Record the current commit hash.
- If the target branch differs from the current branch, ask the user before switching or proceed on the current branch with an explicit note.

After this step, update the state file with `branch`, `target_commit`, and `current_step: 4`.

## 5. Optionally consume related context

Scan `.agents/context/` for reports that help clarify scope, expected behavior, and constraints. It looks for keys matching:

- the current `scope`,
- an inferred ticket key from the scope,
- the current `branch` name.

Common report types: `debrief`, `handoff`, `plan-next`.

These reports are optional. Handle their absence gracefully.

After scanning context, update the state file with `consumed_context` and `current_step: 5`.

## 6. Resolve method

- If `preferences.verification_method` is set and available, use it.
- If unset or ambiguous, present detected options and ask the user.
- Persist the choice in `.agents/config/baseline.yaml`.

For non-UI baselines (API, test, code snapshot), select or adapt the method accordingly.

After selecting the method, update the state file with `selected_method` and `current_step: 6`.

## 7. Resolve target and authentication

- For UI or API methods, resolve the target URL or endpoint.
- For code snapshots, resolve the files or directories.
- Check if the target requires authentication and configure it. See [AUTH.md](AUTH.md).

After this step, update the state file with `target`, `auth_method`, and `current_step: 7`.

## 8. Capture state

Execute the chosen method to capture the current state. Gather evidence such as screenshots, logs, responses, or file contents.

After capturing evidence, update the state file with `artifact_dir` and `current_step: 8`.

## 9. Generate artifacts

Save captured evidence to `.agents/context/baseline/{scope}-{branch}/`.

After this step, update the state file with `current_step: 9`.

## 10. Generate reports

Write the canonical Markdown report at `.agents/context/baseline/{scope}-{branch}.md`. Optionally generate an HTML gallery.

After generating reports, update the state file with `report_path` and `current_step: 10`.

## 11. Curate notes

Update `.agents/config/baseline.yaml` with any workarounds, preferences, gotchas, or decisions discovered.

After curating notes, archive the state file to `.agents/context/baseline/.state/{scope}-{branch}-completed.json` or remove it.

## Hard-stop conditions

Stop and consult the user if:

- Scope cannot be resolved.
- The target branch is missing or unreachable.
- The target URL, endpoint, or files are unreachable.
- No capture method is available and the user declines manual fallback.
- Authentication is required but cannot be resolved.
