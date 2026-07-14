# Baseline Workflow

Detailed workflow for the `baseline` skill.

After each step, write the state file at `{context_dir}/baseline/.state/{scope}-{branch}.json` with the current step and any resolved values.

## 0. Resume if fresh

Check `{context_dir}/baseline/.state/{scope}-{branch}.json`.

- If it exists and `branch`/`commit` still match, resume from `current_step`.
- If it is stale, archive it with `.stale` and start fresh.
- If a worker returned `needs_input`, present the recorded question and resume after the user answers.

## 1. Load config

Read `{config_dir}/baseline.yaml` and `{config_dir}/shared.yaml` if they exist.

## 2. Detect required capabilities

Check that `git` and `python3` are available. If either is missing, stop and report `blocked`. Do not scan the full tooling catalog at this stage.

## 3. Resolve scope

- Use the user-provided scope if available.
- If none, scan `{context_dir}/` for context reports whose frontmatter might imply a scope.
- If still ambiguous, stop and ask.

## 4. Resolve branch and commit

- Use the current branch unless the user specifies another.
- Record the current commit hash.
- If the target branch differs from the current branch, ask before switching or proceed with an explicit note.

## 5. Consume related context

Scan `{context_dir}/` for reports whose frontmatter matches `scope`, `ticket`/`key`, or `branch`.

Exclude:
- Reports whose `skill` frontmatter is `baseline`.
- Files inside `{context_dir}/baseline/`.

Handle missing reports gracefully.

## 6. Resolve method

- Evaluate methods broadly based on project type and scope.
- Select the best method.
- Check tooling for the selected method only, using `references/TOOLING.md`.
- If tooling is missing, explain the gap and offer: configure a recommended tool, switch to an alternative method, or use manual fallback.
- Persist the choice in `{config_dir}/baseline.yaml` only after explicit confirmation.

## 7. Resolve target and authentication

- For `ui-browser` and `api-http` methods, resolve the target URL or endpoint.
- For `code-snapshot` methods, resolve the files or directories.
- Configure authentication if needed. See [AUTH.md](AUTH.md).

## 8. Capture state

Execute the chosen method. Gather evidence such as screenshots, logs, responses, or file contents. Record the key findings needed to synthesize the report summary.

## 9. Generate artifacts and reports

Save captured evidence to `{context_dir}/baseline/{scope}-{branch}/`.

Write the canonical report at `{context_dir}/baseline/{scope}-{branch}.md` with:

- All required frontmatter: `skill`, `version`, `scope`, `branch`, `commit`, `method`, `baselined_at`, `type`, `summary`.
- `reproducible` only when `type` is `bug`.
- Relative artifact references.

Optionally generate an HTML gallery.

## 10. Curate notes and finalize

Update `{config_dir}/baseline.yaml` with workarounds, preferences, tooling choices, or decisions discovered. Archive or remove the state file.

## Hard-stop conditions

Stop and consult the user if:

- Scope cannot be resolved.
- The target branch is missing or unreachable.
- The target URL, endpoint, or files are unreachable.
- A required capability (`git` or `python3`) is missing.
- The selected method has no available tooling and the user declines all alternatives (including manual fallback).
- Authentication is required but cannot be resolved.
