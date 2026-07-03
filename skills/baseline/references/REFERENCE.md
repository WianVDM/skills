# Baseline Reference

Detailed checklists, report templates, and artifact conventions for the `baseline` skill.

---

## Bug reproduction checklist

- [ ] Resolve scope and confirm it is unambiguous.
- [ ] Confirm the target branch and record the current commit.
- [ ] Verify the chosen capture method is working.
- [ ] Start the dev server or target service if needed and if user preference allows.
- [ ] Navigate to the relevant route, endpoint, or code location.
- [ ] Execute the exact reproduction steps from consumed context or user input.
- [ ] Capture evidence of the initial state.
- [ ] Capture evidence after each reproduction step.
- [ ] Capture evidence of the final or error state.
- [ ] Capture console errors, network errors, or response logs if applicable.
- [ ] Note any deviation from the behavior described in consumed context.
- [ ] Document whether the bug is reproducible.

## Feature baseline checklist

- [ ] Resolve scope and confirm it is unambiguous.
- [ ] Confirm the target branch and record the current commit.
- [ ] Verify the chosen capture method is working.
- [ ] Start the dev server or target service if needed and if user preference allows.
- [ ] Navigate to the affected page, endpoint, or code location.
- [ ] Capture evidence of the current state.
- [ ] Identify all elements that will change.
- [ ] Note existing similar functionality.
- [ ] Document current data and empty states.
- [ ] Capture errors or anomalies.

## API baseline checklist

- [ ] Resolve scope and confirm the endpoint or contract.
- [ ] Confirm the target branch and record the current commit.
- [ ] Verify the chosen HTTP client or API method is working.
- [ ] Start the target service if needed and if user preference allows.
- [ ] Capture the request and response for the baseline call.
- [ ] Document headers, status codes, and response bodies.
- [ ] Note any authentication or environment requirements.
- [ ] Record deviations from the expected contract.

## Code snapshot checklist

- [ ] Resolve scope and confirm the files or modules to capture.
- [ ] Confirm the target branch and record the current commit.
- [ ] Capture the current state of the relevant files or directories.
- [ ] Include dependency or import relationships if relevant.
- [ ] Document any TODOs, FIXMEs, or known issues in scope.
- [ ] Record the reason for the snapshot.

## Hard-stop conditions

Stop immediately and flag if:

- Scope cannot be resolved unambiguously.
- The target branch is missing or cannot be checked out.
- The target is unreachable and cannot be resolved.
- The capture method stops responding or fails without a viable fallback.
- Authentication fails and no fallback is available.
- The reproduction steps do not produce the described behavior and the user cannot clarify.

---

## Artifact directory structure

All artifacts must be saved under `.agents/context/baseline/{scope-key}/` or the directory named by the report filename:

```text
.agents/context/baseline/
├── {scope}-{branch}.md
├── {scope}-{branch}.html        # optional
└── {scope}-{branch}/
    ├── screenshots/
    │   ├── initial.png
    │   ├── step-1.png
    │   ├── step-2.png
    │   └── final.png
    ├── logs/
    │   ├── console.log
    │   └── network.log
    ├── requests/
    │   ├── request.json
    │   └── response.json
    ├── code/
    │   └── affected-files.md
    ├── dom-snapshot.json
    └── session/
        └── cookies.json
```

### Rules

- Screenshots and step artifacts are named by step, not by timestamp.
- If the tool cannot save directly to this path, capture to a temporary location and move the files afterward.
- The main `.md` report references artifacts using relative paths from the report file.
- On resume, reuse existing artifacts when they are still fresh; overwrite when re-capturing.
- Keep the artifact directory name consistent with the report filename.

---

## Markdown report template

```markdown
---
skill: baseline
version: 3
scope: auth-guard-race-condition
branch: main
commit: abc1234
method: playwright-mcp
consumed_context:
  - .agents/context/debrief/OC-4644.md
baselined_at: 2026-06-26T08:42:00Z
type: bug
reproducible: true
artifacts_dir: auth-guard-race-condition-main
summary: "Auth guard redirects to login during token refresh."
---

# Baseline: auth-guard-race-condition — Auth guard race condition

## Environment
- Branch: main
- Commit: abc1234
- Dev server: http://localhost:4200
- Browser viewport: 1280x720
- Method: Playwright MCP
- Scope: auth-guard-race-condition

## Authentication
- Method: session-file
- Session: `.agents/context/baseline/auth-guard-race-condition-main/session/cookies.json`

## Reproduction steps
1. Navigate to `/login`.
2. Enter valid credentials and submit.
3. Quickly navigate to `/dashboard` before the token refresh completes.

## Screenshots
- [initial](auth-guard-race-condition-main/screenshots/initial.png): Login page loaded.
- [step-1](auth-guard-race-condition-main/screenshots/step-1.png): After submitting credentials.
- [final](auth-guard-race-condition-main/screenshots/final.png): Redirected to login instead of dashboard.

## Console errors
```
No errors.
```

## Network errors
```
No errors.
```

## Findings
The bug is reproducible. Navigating to `/dashboard` during token refresh causes the auth guard to redirect back to `/login`.

## Deviation from consumed context
None. Behavior matches the description in the debrief report.
```

### Template notes

- `scope` and `branch` are required in the filename and frontmatter.
- `commit` identifies the exact code state at capture time.
- `method` records how the baseline was captured.
- `consumed_context` lists any reports that informed the baseline. Omit if none were read.
- Keep the body focused on evidence, findings, and deviations.

---

## HTML gallery template

The optional HTML gallery is a self-contained, human-readable view of the baseline. It is generated alongside the Markdown report when `output.default_format` is set to `html-both`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Baseline: auth-guard-race-condition</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-size: 1.75rem; }
    h2 { font-size: 1.25rem; margin-top: 2rem; }
    figure { margin: 1rem 0; }
    img { max-width: 100%; border: 1px solid #ccc; }
    figcaption { font-size: 0.9rem; color: #555; margin-top: 0.25rem; }
    pre { background: #f5f5f5; padding: 1rem; overflow-x: auto; }
    .meta { color: #555; }
  </style>
</head>
<body>
  <h1>Baseline: auth-guard-race-condition — Auth guard race condition</h1>
  <p class="meta">
    <strong>Branch:</strong> main ·
    <strong>Commit:</strong> abc1234 ·
    <strong>Type:</strong> bug ·
    <strong>Reproducible:</strong> true ·
    <strong>Baselined at:</strong> 2026-06-26T08:42:00Z
  </p>

  <h2>Environment</h2>
  <ul>
    <li>Branch: main</li>
    <li>Commit: abc1234</li>
    <li>Dev server: http://localhost:4200</li>
    <li>Viewport: 1280x720</li>
    <li>Method: Playwright MCP</li>
  </ul>

  <h2>Reproduction steps</h2>
  <ol>
    <li>Navigate to <code>/login</code>.</li>
    <li>Enter valid credentials and submit.</li>
    <li>Quickly navigate to <code>/dashboard</code> before token refresh completes.</li>
  </ol>

  <h2>Screenshots</h2>

  <figure>
    <img src="auth-guard-race-condition-main/screenshots/initial.png" alt="Initial state">
    <figcaption>Initial state: login page loaded.</figcaption>
  </figure>

  <figure>
    <img src="auth-guard-race-condition-main/screenshots/step-1.png" alt="After submitting credentials">
    <figcaption>After submitting credentials.</figcaption>
  </figure>

  <figure>
    <img src="auth-guard-race-condition-main/screenshots/final.png" alt="Final state">
    <figcaption>Final state: redirected back to login instead of dashboard.</figcaption>
  </figure>

  <h2>Console errors</h2>
  <pre>No errors.</pre>

  <h2>Network errors</h2>
  <pre>No errors.</pre>

  <h2>Findings</h2>
  <p>The bug is reproducible. Navigating to <code>/dashboard</code> during token refresh causes the auth guard to redirect back to <code>/login</code>.</p>
</body>
</html>
```

### HTML rules

- The HTML file lives next to the Markdown report.
- It references artifacts using relative paths.
- It is for human consumption only. Other skills should read the `.md` report.
- Keep styling inline and minimal so the file is self-contained.

---

## Versioning and migration guidance

### Report version

Reports include `version: 3` to match the producing skill's major version. Consumers should inspect this field and adjust parsing if the version differs from their expected schema.

### Migrating older reports

Reports produced by earlier versions of the skill may:

- Use `ticket` instead of `scope`.
- Omit `branch` or `commit`.
- Name files with `{ticket-key}-{slug}.md` instead of `{scope}-{branch}.md`.

When encountering an older report, treat it as potentially stale. Prefer re-capturing with the current skill version. If re-capture is not possible, record the migration path in the report body and update the frontmatter where feasible.

### Breaking changes to track

If a future version changes the report schema, config schema, or file naming convention, bump the skill version and document:

- What changed.
- Whether older reports remain compatible.
- How to migrate or mark stale reports.

Keep the skill version in the frontmatter of `SKILL.md` in sync with the report `version`.
