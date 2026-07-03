# Baseline Workflow

Detailed workflow for the `baseline` skill.

After each step, write the state file at `.agents/context/baseline/.state/{scope}-{branch}.json` with the current step and any resolved values.

## 0. Resume if fresh

Check `.agents/context/baseline/.state/{scope}-{branch}.json`.

- If it exists and `branch`/`commit` still match, resume from `current_step`.
- If it is stale, archive it with `.stale` and start fresh.
- If a worker returned `needs_input`, present the recorded question and resume after the user answers.

## 1. Load config

Read `.agents/config/baseline.yaml` and `.agents/config/shared.yaml` if they exist.

## 2. Detect capabilities

Identify available capture methods (UI, API, test, code snapshot, manual). See [CAPABILITIES.md](CAPABILITIES.md).

## 3. Resolve scope

- Use the user-provided scope if available.
- If none, scan `.agents/context/` for context reports whose frontmatter might imply a scope.
- If still ambiguous, stop and ask.

## 4. Resolve branch and commit

- Use the current branch unless the user specifies another.
- Record the current commit hash.
- If the target branch differs from the current branch, ask before switching or proceed with an explicit note.

## 5. Consume related context

Scan `.agents/context/` for reports whose frontmatter matches `scope`, `ticket`/`key`, or `branch`.

Exclude:
- Reports whose `skill` frontmatter is `baseline`.
- Files inside `.agents/context/baseline/`.

Handle missing reports gracefully.

## 6. Resolve method

- Use `preferences.verification_method` if set and available.
- Otherwise, present detected options and ask the user.
- Persist the choice in `.agents/config/baseline.yaml`.

## 7. Resolve target and authentication

- For UI/API methods, resolve the target URL or endpoint.
- For code snapshots, resolve the files or directories.
- Configure authentication if needed. See [AUTH.md](AUTH.md).

## 8. Capture state

Execute the chosen method. Gather evidence such as screenshots, logs, responses, or file contents. Record the key findings needed to synthesize the report summary.

## 9. Generate artifacts and reports

Save captured evidence to `.agents/context/baseline/{scope}-{branch}/`.

Write the canonical report at `.agents/context/baseline/{scope}-{branch}.md` with:

- All required frontmatter: `skill`, `version`, `scope`, `branch`, `commit`, `method`, `baselined_at`, `type`, `summary`.
- `reproducible` only when `type` is `bug`.
- Relative artifact references.

Optionally generate an HTML gallery.

## 10. Curate notes and finalize

Update `.agents/config/baseline.yaml` with workarounds, preferences, gotchas, or decisions discovered. Archive or remove the state file.

## Hard-stop conditions

Stop and consult the user if:

- Scope cannot be resolved.
- The target branch is missing or unreachable.
- The target URL, endpoint, or files are unreachable.
- No capture method is available and the user declines manual fallback.
- Authentication is required but cannot be resolved.
